import sqlite3

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, List, NamedTuple

from .node_config import NodeConfig
from .vector_clock import VectorClock

_SQLITE_TS_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

def _dt_sqlite_ts(dt: datetime):
    with_usecs = dt.strftime(_SQLITE_TS_FORMAT)
    # truncate to milliseconds
    with_msecs = with_usecs[:-3]
    return with_msecs + "Z"


def _sqlite_ts_dt(sqlite_ts: str):
    with_usecs = sqlite_ts[:-1] + "000"
    return datetime.strptime(with_usecs, _SQLITE_TS_FORMAT)


def _default_utcnow():
    return datetime.utcnow()


class EntityKey(NamedTuple):
    entity_name: str
    entity_id: str


class Entry(NamedTuple):
    timestamp: datetime
    entity_name: str
    entity_id: str
    entity: Any
    vclock: VectorClock


class Change(NamedTuple):
    # type is "modified", "deleted", "conflict"
    # TODO(fyhuang): do we need "deleted"?
    type: str
    entity_name: str
    entity_id: str
    entity: Any


class Log(object):
    CURR_VERSION = "1"

    def __init__(self, connection: sqlite3.Connection, utcnow: Callable[[], datetime] = _default_utcnow) -> None:
        self.conn = connection
        self.utcnow = utcnow
        # check presence of tables
        self.first_time_setup()
        # make sure that version matches
        c = self.conn.cursor()
        c.execute("SELECT value FROM metadata WHERE key = ?", ("version",))
        version = c.fetchone()[0]
        if version != Log.CURR_VERSION:
            raise RuntimeError("Cannot load DB with version {} (code is version {})"
                    .format(version, Log.CURR_VERSION))

    def first_time_setup(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS metadata (
            key TEXT NOT NULL PRIMARY KEY,
            value TEXT NOT NULL
        )''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS nodes (
            clock_id INT NOT NULL PRIMARY KEY,
            display_name TEXT NOT NULL,
            last_seen_ts DATETIME NOT NULL
        )''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS log (
            timestamp DATETIME NOT NULL PRIMARY KEY,
            entity_name TEXT,
            entity_id TEXT,
            entity BLOB NOT NULL,
            vclock BLOB NOT NULL
        )''')

        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO metadata VALUES (?, ?)",
                ("version", "1"))

    def _register_node(self, node_config: NodeConfig):
        with self.conn:
            self.conn.execute('INSERT OR IGNORE INTO nodes VALUES (?, ?, ?)',
                (node_config.clock_id, node_config.display_name, _dt_sqlite_ts(datetime(1970, 1, 1))))

    def _get_known_nodes(self) -> List[NodeConfig]:
        result = []
        c = self.conn.cursor()
        for row in c.execute("SELECT clock_id, display_name FROM nodes"):
            result.append(NodeConfig(row[0], row[1]))
        return result

    def _oldest_node_ts(self) -> datetime:
        c = self.conn.cursor()
        c.execute("SELECT last_seen_ts FROM nodes ORDER BY last_seen_ts ASC LIMIT 1")
        return _sqlite_ts_dt(c.fetchone()[0])

    def _newest_timestamp(self) -> Optional[datetime]:
        c = self.conn.cursor()
        result = c.execute("SELECT timestamp FROM log ORDER BY timestamp DESC LIMIT 1").fetchone()
        if result is None:
            return None
        return _sqlite_ts_dt(result[0])

    def _newest_vclock(self) -> VectorClock:
        c = self.conn.cursor()
        result = c.execute("SELECT vclock FROM log ORDER BY timestamp DESC LIMIT 1").fetchone()
        if result is None:
            return VectorClock()
        return VectorClock.from_packed(result[0])

    def _get_entries_since(self, dt: datetime) -> List[Entry]:
        result = []
        c = self.conn.cursor()
        for row in c.execute("SELECT * FROM log WHERE timestamp >= ? ORDER BY timestamp ASC", (_dt_sqlite_ts(dt),)):
            result.append(Entry(_sqlite_ts_dt(row[0]), row[1], row[2], row[3], VectorClock.from_packed(row[4])))
        return result

    def _get_latest_entry_per_entity(self) -> Dict[EntityKey, Entry]:
        result = {}
        c = self.conn.cursor()
        c.execute("""
        SELECT log.*
        FROM
          (
            SELECT MAX(timestamp) AS timestamp, entity_name, entity_id
            FROM log
            GROUP BY entity_name, entity_id
          ) AS last_ts
        INNER JOIN log
        ON log.timestamp = last_ts.timestamp
        """)
        for row in c:
            result[EntityKey(row[1], row[2])] = Entry(
                _sqlite_ts_dt(row[0]), row[1], row[2], row[3], VectorClock.from_packed(row[4])
            )
        return result

    def add_entry(self, node_config: NodeConfig, entity_name: str, entity_id: str, entity: Any) -> None:
        self._register_node(node_config)

        now = self.utcnow()
        newest = self._newest_timestamp()
        if newest is not None and now < newest:
            raise RuntimeError("Entry ({}) would not be the newest entry ({}), too much clock skew?"
                    .format(now, newest))

        new_clock = self._newest_vclock()
        new_clock.increment(node_config.clock_id)

        with self.conn:
            self.conn.execute("INSERT INTO log VALUES (?, ?, ?, ?, ?)",
                    (_dt_sqlite_ts(now), entity_name, entity_id, entity, new_clock.to_packed()))
            self.conn.execute("UPDATE nodes SET last_seen_ts = :ts WHERE clock_id = :id",
                    {"id": node_config.clock_id, "ts": _dt_sqlite_ts(now)})

    def detect_changes(self, other: 'Log') -> List[Change]:
        our_latest = self._get_latest_entry_per_entity()
        other_latest = self._get_latest_entry_per_entity()

        all_entity_keys = set(our_latest.keys()) | set(other_latest.keys())
        changes: List[Change] = []

        import pdb; pdb.set_trace()

        for key in all_entity_keys:
            default_entry = Entry(datetime.fromtimestamp(0), key.entity_name, key.entity_id, None, VectorClock())
            our_entry = our_latest.get(key, default_entry)
            other_entry = other_latest.get(key, default_entry)
            relation = our_entry.vclock.compare(other_entry.vclock)

            if relation == "equal":
                continue
            elif relation == "after":
                # our entity is newer
                continue
            elif relation == "before":
                # entity was updated in "other"
                if other_entry.entity is None:
                    # entity was deleted
                    change_type = "deleted"
                else:
                    change_type = "modified"
                changes.append(Change(change_type, key.entity_name, key.entity_id, other_entry.entity))
            elif relation == "concurrent":
                changes.append(Change("conflict", key.entity_name, key.entity_id, other_entry.entity))

        return changes

    def merge_from(self, other: 'Log'):
        # merge entries from other log and add a merge entry to indicate merge success
        pass

    def collect_garbage(self):
        pass
