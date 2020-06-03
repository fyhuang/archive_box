import sqlite3
import datetime
import re

from typing import Union

_CREATE_TABLE_RE = re.compile(r'CREATE TABLE( IF NOT EXISTS)? (?P<tname>\w[\d\w]*) \(')
_CREATE_VIRTUAL_TABLE_RE = re.compile(r'CREATE VIRTUAL TABLE( IF NOT EXISTS)? (?P<tname>\w[\d\w]*) USING (\w+) \(')

# TODO(fyhuang): write a test
def ensure_table_matches(conn: sqlite3.Connection, create_table_schema: str) -> None:
    # throws exception if the db already contains a table whose schema doesn't
    # match the one given by `create_table_schema`

    m = None
    schema_res = [_CREATE_TABLE_RE, _CREATE_VIRTUAL_TABLE_RE]
    for regex in schema_res:
        m = regex.match(create_table_schema)
        if m is not None:
            break

    if m is None:
        raise RuntimeError("Unable to parse schema")
    table_name = m.group("tname")
    normalized_schema = create_table_schema.replace("IF NOT EXISTS ", "")

    c = conn.cursor()
    row = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
    if row is None:
        conn.execute(create_table_schema)
        return

    existing_schema = row[0]
    if existing_schema != normalized_schema:
        raise RuntimeError("Table in DB doesn't match declared schema")


def parse_timestamp(sqlite_ts: Union[str, datetime.datetime]) -> datetime.datetime:
    if isinstance(sqlite_ts, datetime.datetime):
        return sqlite_ts

    # from python3/Lib/sqlite3/dbapi2.py:register_adapters_and_converters()
    #datepart, timepart = sqlite_ts.split(" ")
    #year, month, day = map(int, datepart.split("-"))
    #timepart_full = timepart.split(".")
    #hours, minutes, seconds = map(int, timepart_full[0].split(":"))
    #if len(timepart_full) == 2:
    #    microseconds = int('{:0<6.6}'.format(timepart_full[1]))
    #else:
    #    microseconds = 0
 
    #result = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)

    # TODO(fyhuang): this is not very general
    naive_dt_str, _, tzstr = sqlite_ts.partition("+")
    naive_dt = datetime.datetime.strptime(naive_dt_str, "%Y-%m-%d %H:%M:%S.%f")
    if tzstr is None:
        return naive_dt

    tzhours, _, tzmins = tzstr.partition(":")
    tzdelta = datetime.timedelta(hours=int(tzhours), minutes=int(tzmins))
    return naive_dt.replace(tzinfo=datetime.timezone(tzdelta))
