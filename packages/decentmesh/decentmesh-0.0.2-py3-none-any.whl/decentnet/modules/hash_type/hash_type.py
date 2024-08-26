from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.modules.pow.computation_slow import hash_func

from decentnet.modules.pow.difficulty import Difficulty


class MemoryHash:
    def __init__(self, diff: Difficulty, data: bytes):
        self.diff: Difficulty = diff
        self.value: bytes = hash_func(data, diff)

    def __eq__(self, other):
        if isinstance(other, MemoryHash):
            return self.diff == other.diff and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.diff, self.value))

    def __repr__(self):
        return f"MemoryHash(diff={self.diff}, value={self.value.hex()})"

    def recompute(self, data: bytes):
        self.value: bytes = hash_func(data, self.diff)

    def value_as_hex(self):
        return self.value.hex()[2:].zfill(self.diff.hash_len_chars * 2)

    def value_as_int(self) -> int:
        return int.from_bytes(self.value, ENDIAN_TYPE)
