import logging
from dataclasses import dataclass

from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


@dataclass
class Difficulty:
    t_cost: int
    m_cost: int
    p_cost: int
    n_bits: int
    hash_len_chars: int

    def to_bytes(self) -> bytes:
        return (
                self.t_cost.to_bytes(8, byteorder=ENDIAN_TYPE, signed=False).zfill(8) +
                self.m_cost.to_bytes(8, byteorder=ENDIAN_TYPE, signed=False).zfill(8) +
                self.p_cost.to_bytes(8, byteorder=ENDIAN_TYPE, signed=False).zfill(8) +
                self.n_bits.to_bytes(1, byteorder=ENDIAN_TYPE, signed=False) +
                self.hash_len_chars.to_bytes(1, byteorder=ENDIAN_TYPE, signed=False)
        )

    @classmethod
    def from_bytes(cls, difficulty_bytes: bytes):
        t_cost = int.from_bytes(difficulty_bytes[0:8], byteorder=ENDIAN_TYPE,
                                signed=False)
        m_cost = int.from_bytes(difficulty_bytes[8:16], byteorder=ENDIAN_TYPE,
                                signed=False)
        p_cost = int.from_bytes(difficulty_bytes[16:24], byteorder=ENDIAN_TYPE,
                                signed=False)
        n_bits = int.from_bytes(difficulty_bytes[24:25], byteorder=ENDIAN_TYPE,
                                signed=False)
        hash_len_chars = int.from_bytes(difficulty_bytes[25:26], byteorder=ENDIAN_TYPE,
                                        signed=False)

        return cls(t_cost, m_cost, p_cost, n_bits, hash_len_chars)

    def __eq__(self, other):
        """
        Compares all.yaml attributes of the Difficulty instance except for the n_bits attribute.
        """
        if isinstance(other, Difficulty):
            return (self.t_cost, self.m_cost, self.p_cost, self.hash_len_chars) == \
                (other.t_cost, other.m_cost, other.p_cost, other.hash_len_chars)
        return False

    def __repr__(self):
        return f"Difficulty(t_cost={self.t_cost}," \
               f" m_cost={self.m_cost}," \
               f" p_cost={self.p_cost}" \
               f", n_bits={self.n_bits}," \
               f" hash_len_chars={self.hash_len_chars})"

    def __hash__(self):
        return hash(
            (self.t_cost, self.m_cost, self.p_cost, self.n_bits, self.hash_len_chars))

    def __iter__(self):
        yield from [self.t_cost, self.m_cost, self.p_cost, self.n_bits,
                    self.hash_len_chars]

    def __str__(self):
        return f"{self.t_cost}:{self.m_cost}:{self.p_cost}:{self.n_bits}:{self.hash_len_chars}"

    def __post_init__(self):
        if (req_m_cost := 8 * self.p_cost) > self.m_cost:
            logger.debug(
                f"Memory too low increasing from {self.m_cost} to {req_m_cost}")
            self.m_cost = req_m_cost
