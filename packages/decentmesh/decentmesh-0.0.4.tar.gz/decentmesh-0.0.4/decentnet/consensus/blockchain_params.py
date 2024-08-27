"""
Blockchain Parameters
"""
from dataclasses import dataclass

from decentnet.consensus.block_sizing import HASH_LEN
from decentnet.modules.pow.difficulty import Difficulty

SAVE_BLOCKS_TO_DB_DEFAULT = False

@dataclass
class BlockchainParams:
    default_salt = b"Knz3z0&PavluT0m"
    default_salt_len = len(default_salt)
    default_genesis_msg = "CONNECTED"
    block_version = bytes([0x24])
    blockchain_version = 1
    seed_difficulty = Difficulty(16, 8, 1, 16, HASH_LEN)
    low_diff = Difficulty(1, 8, 1, 8, HASH_LEN)
    max_hosts = 65536
