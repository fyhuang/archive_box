import collections
import struct

from typing import Optional, Dict

class VectorClock(object):
    def __init__(self, clock: Optional[Dict[int, int]] = None):
        self.clock: Dict[int, int] = collections.defaultdict(lambda: 0)
        if clock is not None:
            self.clock.update(clock)

    # the packed format is a simple list of 64-bit integer tuples
    @staticmethod
    def from_packed(packed_bytes: bytes) -> 'VectorClock':
        result = VectorClock()
        for (k, v) in struct.iter_unpack("!QQ", packed_bytes):
            result.clock[k] = v
        return result

    def to_packed(self) -> bytes:
        result = bytearray()
        for k,v in self.clock.items():
            result.extend(struct.pack("!QQ", k, v))
        return bytes(result)

    def increment(self, idx: int):
        self.clock[idx] += 1

    def compare(self, other: 'VectorClock') -> str:
        # returns self X other, where X is one of ("before", "equal", "after", "concurrent")
        all_keys = set(self.clock.keys()) | set(other.clock.keys())
        all_less = True
        all_more = True

        for k in all_keys:
            if self.clock[k] < other.clock[k]:
                all_more = False
            elif self.clock[k] > other.clock[k]:
                all_less = False

        if all_less and all_more:
            return "equal"
        elif all_less and not all_more:
            return "before"
        elif not all_less and all_more:
            return "after"
        else: # all_less == all_more == False
            return "concurrent"

    def merge_from(self, other: 'VectorClock'):
        all_keys = set(self.clock.keys()) | set(other.clock.keys())
        for k in all_keys:
            self.clock[k] = max(self.clock[k], other.clock[k])

    def __eq__(self, other):
        if not isinstance(other, VectorClock):
            return False
        return self.compare(other) == "equal"
