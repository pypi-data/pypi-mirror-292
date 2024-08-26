import logging
from typing import Optional

import pyximport
import rich

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.hash_type.hash_type import MemoryHash
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.pow.difficulty import Difficulty

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)

pyximport.install()
try:
    from decentnet.modules.pow.computation_fast import compute_pow  # noqa
except ImportError as ex:
    rich.print(f"[red]POW Operating in low hashrate mode, more instructions: {ex}[/red]")
    from decentnet.modules.pow.computation_slow import compute_pow


class PoW:
    def __init__(self, input_hash: MemoryHash, diff: Difficulty):
        self.finished_nonce: Optional[int] = None
        self.finished_hash: Optional[MemoryHash] = None
        self.previous_hash = input_hash
        self.difficulty = diff
        self.compute_time = None

    def compute(self, start_nonce=0):
        hash_t = self.previous_hash
        nonce = compute_pow(self.difficulty.n_bits, hash_t, start_nonce)

        self.finished_hash = hash_t
        self.finished_nonce = nonce

        return self
