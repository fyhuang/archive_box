import datetime
from typing import NamedTuple

class StoredStat(NamedTuple):
    size_bytes: int
    upload_time: datetime.datetime
