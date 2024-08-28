import datetime
import functools
import logging
import struct
from typing import Optional, Union

import rich
from prometheus_client import Gauge

from decentnet.consensus.block_sizing import MERGED_DIFFICULTY_BYTE_LEN, HASH_LEN, \
    INDEX_SIZE, VERSION_SIZE, NONCE_SIZE, TIMESTAMP_SIZE
from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import registry
from decentnet.modules.blockchain.hasht import HashT
from decentnet.modules.compression.wrapper import CompressionWrapper
from decentnet.modules.hash_type.hash_type import MemoryHash
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.pow.difficulty import Difficulty
from decentnet.modules.pow.pow import PoW
from decentnet.modules.timer.timer import Timer

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)

data_header_ratio = Gauge('data_header_ratio', 'Header/Data Ratio', registry=registry)


class Block:
    index: int
    previous_hash: bytes = None
    version: bytes
    diff: Difficulty
    data: bytearray
    timestamp: float
    nonce: int
    _hash: Optional[MemoryHash]
    ttc: float
    signature: Optional[str] = None

    def __init__(self, index: int, prev_hash: bytes,
                 difficulty: Difficulty,
                 data: Union[bytearray, bytes]):
        self.index = index
        self.previous_hash = prev_hash
        self.data = data
        self.diff = difficulty
        self.timestamp = datetime.datetime.now().timestamp()
        self.version = BlockchainParams.block_version
        self.nonce = 0
        self.signature = None

    def __str__(self):
        result = f"Block #{self.index}\n" \
                 f"Previous Hash: {self.previous_hash.hex()[2:].zfill(HASH_LEN) if self.index != 0 else 'GENESIS BLOCK'}\n" \
                 f"Version: {int.from_bytes(self.version, ENDIAN_TYPE)}\n" \
                 f"Difficulty: {self.diff}\n" \
                 f"Data: {str(self.data)}\n" \
                 f"Timestamp: {self.timestamp}\n" \
                 f"Nonce: {self.nonce}\n"

        if hasattr(self, "_hash"):
            result += f"Hash: {self.hash.hex()[2:].zfill(HASH_LEN)}\n"

        return result

    @property
    def hash(self):
        return self.get_hash()

    def get_hash(self) -> bytes:
        barr = bytearray(self._hash.value)
        return bytes(barr)

    def compute_hash(self) -> MemoryHash:
        self._hash = MemoryHash(self.diff, self.to_bytes())
        return self._hash

    @functools.lru_cache(maxsize=256, typed=False)
    def to_bytes(self) -> bytes:
        index_bytes = self.index.to_bytes(8, byteorder=ENDIAN_TYPE, signed=False).zfill(
            INDEX_SIZE)
        version_bytes = self.version
        diff_bytes = self.diff.to_bytes().zfill(MERGED_DIFFICULTY_BYTE_LEN)
        previous_hash_bytes = self.previous_hash.zfill(HASH_LEN)
        nonce_bytes = self.nonce.to_bytes(NONCE_SIZE, byteorder=ENDIAN_TYPE,
                                          signed=False).zfill(
            NONCE_SIZE)
        timestamp_bytes = struct.pack('d', self.timestamp).zfill(TIMESTAMP_SIZE)

        raw_data = self.data
        try:
            compressed_data = CompressionWrapper.compress_lz4(
                raw_data)  # TODO: Encrypt data
        except TypeError as ex:
            logger.critical(f"Invalid data type in block {self.data}")
            raise ex

        packed_block = (index_bytes + version_bytes + diff_bytes + previous_hash_bytes +
                        nonce_bytes + timestamp_bytes + compressed_data)  # Speed up compression

        packed_block_len = len(packed_block)
        compressed_data_len = len(compressed_data)

        data_header_ratio.set(
            (packed_block_len - compressed_data_len) / compressed_data_len)

        logger.debug(f"Packed Block into {packed_block_len} bytes")
        return packed_block

    @classmethod
    def from_bytes(cls, compressed_block_bytes: bytes, compute_hash: bool = False):
        block = cls.__new__(cls)

        block_bytes = compressed_block_bytes

        cursor = 0

        block.index = int.from_bytes(block_bytes[:INDEX_SIZE], byteorder=ENDIAN_TYPE,
                                     signed=False)
        cursor += INDEX_SIZE

        block.version = block_bytes[cursor].to_bytes(VERSION_SIZE, ENDIAN_TYPE,
                                                     signed=False)
        cursor += VERSION_SIZE
        block.diff = Difficulty.from_bytes(
            block_bytes[cursor:cursor + MERGED_DIFFICULTY_BYTE_LEN])

        cursor += MERGED_DIFFICULTY_BYTE_LEN

        block.previous_hash = block_bytes[cursor:cursor + HASH_LEN]
        cursor += HASH_LEN

        block.nonce = int.from_bytes(
            block_bytes[cursor:cursor + NONCE_SIZE],
            byteorder=ENDIAN_TYPE, signed=False)
        cursor += NONCE_SIZE
        block.timestamp = cls.unpack_timestamp(
            block_bytes[cursor:cursor + TIMESTAMP_SIZE])
        cursor += TIMESTAMP_SIZE
        compressed_data = block_bytes[cursor:]

        block.data = CompressionWrapper.decompress_lz4(compressed_data)
        # Compute the hash after reconstructing the block
        if compute_hash:
            block._hash = MemoryHash(block.diff, block.to_bytes())
        return block

    @classmethod
    def unpack_timestamp(cls, timestamp_bytes: bytes) -> float:
        return struct.unpack('d', timestamp_bytes)[0]

    def mine(self, measure=True):
        logger.debug(f"Mining block #{self.index}")
        if measure:
            t = Timer()

        a = self.compute_hash()
        pow_tmp = PoW(a, self.diff)
        pow_tmp.compute()
        hash_t = HashT(a.value, pow_tmp.finished_nonce)
        if hash_t.value != pow_tmp.finished_hash.value:
            rich.print("[red]Critical! computed values not consistent[/red]")
        self.nonce = pow_tmp.finished_nonce

        if measure:
            self.ttc = t.stop()
            return hash_t, pow_tmp.finished_nonce, t.stop()
        else:
            return hash_t, pow_tmp.finished_nonce
