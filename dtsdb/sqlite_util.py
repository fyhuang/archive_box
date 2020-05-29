import sqlite3
import datetime
import re

_CREATE_TABLE_RE = re.compile(r'CREATE TABLE( IF NOT EXISTS)? (?P<tname>\w[\d\w]*) \(')

# TODO(fyhuang): write a test
def ensure_table_matches(conn: sqlite3.Connection, create_table_schema: str) -> None:
    # throws exception if the db already contains a table whose schema doesn't
    # match the one given by `create_table_schema`
    m = _CREATE_TABLE_RE.match(create_table_schema)
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


def parse_timestamp(sqlite_ts: str):
    if isinstance(sqlite_ts, datetime.datetime):
        return sqlite_ts

    # from python3/Lib/sqlite3/dbapi2.py:register_adapters_and_converters()
    datepart, timepart = sqlite_ts.split(" ")
    year, month, day = map(int, datepart.split("-"))
    timepart_full = timepart.split(".")
    hours, minutes, seconds = map(int, timepart_full[0].split(":"))
    if len(timepart_full) == 2:
        microseconds = int('{:0<6.6}'.format(timepart_full[1]))
    else:
        microseconds = 0
 
    result = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)
    return result
