import asyncio
import logging
from datetime import datetime
from math import log2
from typing import Set, List, Optional

import cbor2
import pyximport
from prometheus_client import Gauge

from decentnet.consensus.blockchain_params import BlockchainParams, SAVE_BLOCKS_TO_DB_DEFAULT
from decentnet.consensus.cmd_enum import CMD
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import registry
from decentnet.modules.blockchain.block import Block
from decentnet.modules.cryptography.asymetric import AsymCrypt
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import BlockchainTable, BlockTable, BlockSignatureTable
from decentnet.modules.hash_type.hash_type import MemoryHash
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.passgen.passgen import SecurePasswordGenerator
from decentnet.modules.pow.difficulty import Difficulty

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)

pyximport.install()
try:
    from decentnet.modules.convert.byte_to_base64_fast import bytes_to_base64  # noqa
except ImportError as ex:
    logger.warning("Base64 convert module is operating in slow mode")
    from decentnet.modules.convert.byte_to_base64_slow import bytes_to_base64

block_difficulty_bits = Gauge('block_difficulty_bits', 'Difficulty of blockchain bits',
                              registry=registry)
block_difficulty_memory = Gauge('block_difficulty_memory',
                                'Difficulty of blockchain memory', registry=registry)
block_difficulty_time = Gauge('block_difficulty_time', 'Difficulty of blockchain time',
                              registry=registry)
block_difficulty_parallel = Gauge('block_difficulty_parallel',
                                  'Difficulty of blockchain parallel', registry=registry)


class Blockchain:
    _id: int
    chain_hashes: Set[MemoryHash]
    chain: List[Block]
    version: int
    latency: float
    _difficulty: Difficulty

    def __init__(self, genesis_data: Optional[str] = None, save=SAVE_BLOCKS_TO_DB_DEFAULT,
                 difficulty: Difficulty = BlockchainParams.seed_difficulty,
                 owned_pub_key_for_encryption: str | None = None,
                 beam_id: int | None = None,
                 next_difficulty: Difficulty = BlockchainParams.low_diff, name="default"):
        self.pub_key_for_encryption = owned_pub_key_for_encryption
        self._difficulty = difficulty
        self.version = BlockchainParams.blockchain_version
        self.latency = 0
        self.chain_hashes = set()
        self.chain: [Block] = []
        self.save = save
        self.name = name
        self._id = -1

        if save:
            with session_scope() as session:
                b_gen = BlockchainTable(version=self.version, latency=self.latency,
                                        beam_id=beam_id,
                                        difficulty=str(self.difficulty))
                session.add(b_gen)
                session.commit()
                self._id = b_gen.blockchain_id

        if genesis_data:
            if self.pub_key_for_encryption is None:
                logger.warning(
                    "Public key for encryption not provided, data will be not encrypted.")

            seed_block = self.create_genesis(genesis_data.encode("ascii"),
                                             owned_public_key_for_encryption=self.pub_key_for_encryption,
                                             difficulty=difficulty,
                                             next_difficulty=next_difficulty)
            seed_block.mine()
            if not self.insert(seed_block):
                raise Exception("Failed to insert genesis block")

            self.difficulty = next_difficulty

    @classmethod
    def create_genesis(cls, data, owned_public_key_for_encryption: str | None,
                       difficulty: Difficulty = BlockchainParams.seed_difficulty,
                       next_difficulty: Difficulty = BlockchainParams.low_diff):

        genesis_data = cbor2.dumps({"data": data.decode("ascii"),
                                    "new_diff": next_difficulty.to_bytes().decode(
                                        "ascii"),
                                    "enc_pub_key": owned_public_key_for_encryption})
        block = Block(0, b"0", difficulty, genesis_data)
        block.seed_hash = block.compute_hash()
        return block

    @classmethod
    def create_handshake_encryption_block_raw(cls,
                                              public_key_received_for_encryption: str,
                                              bits: int = 192, algorithm: str = "AES",
                                              additional_data: str = "") -> (bytes, bytes):
        """
        Create handshake encryption data for block
        :param additional_data:
        :param public_key_received_for_encryption:
        :param bits:
        :param algorithm:
        :return: handshake block in raw byte format dumped by cbor2, password
        """
        encrypted_password, password = cls._create_handshake_block_base(bits,
                                                                        public_key_received_for_encryption)

        data = cls.convert_handshake_block_dict_to_bytes(
            {"cmd": CMD.HANDSHAKE_ENCRYPTION.value, "key": encrypted_password,
             "data": additional_data,
             "algo": algorithm, "bits": bits})
        return data, password

    @classmethod
    def _create_handshake_block_base(cls, bits: int, public_key_received_for_encryption: str):
        """
        Creates base data for handshake block
        :param bits:
        :param public_key_received_for_encryption:
        :return:
        """
        byte_length = int(bits / 8)
        password = SecurePasswordGenerator(length=byte_length).generate().encode("utf-8")[:byte_length]
        pub_key = AsymCrypt.public_key_from_base64(public_key_received_for_encryption,
                                                   can_encrypt=True)
        encrypted_password_bytes = AsymCrypt.encrypt_message(pub_key,
                                                             password)
        encrypted_password = bytes_to_base64(encrypted_password_bytes)
        return encrypted_password, password

    @classmethod
    def convert_handshake_block_dict_to_bytes(cls, handshake_block: dict) -> bytes:
        return cbor2.dumps(handshake_block)

    @classmethod
    def create_handshake_encryption_block_dict(cls,
                                               public_key_received_for_encryption: str,
                                               bits: int = 192, algorithm: str = "AES",
                                               additional_data: str = "") -> (dict, bytes):
        """
        Create handshake encryption data for block
        :param additional_data:
        :param public_key_received_for_encryption:
        :param bits:
        :param algorithm:
        :return: handshake block in dict format, password
        """
        encrypted_password, password = cls._create_handshake_block_base(bits,
                                                                        public_key_received_for_encryption)

        data = {"cmd": CMD.HANDSHAKE_ENCRYPTION.value, "key": encrypted_password,
                "data": additional_data,
                "algo": algorithm, "bits": bits}
        return data, password

    def get_last(self):
        return self.chain[-1]

    @staticmethod
    def get_next_work_required(requested_diff: Difficulty) -> int:
        """

        Get Required work from Difficulty parameters
        @param requested_diff Input Difficulty
        @return

        :param requested_diff:
        :return:
        """
        return 1 << requested_diff.n_bits

    def validate_next_block(self, block: Block):

        if block.index != len(self.chain):
            logger.error(
                f"Block index is not same as chain length {block.index} != {len(self.chain)}")
            return False
        if block.index > 0 and block.previous_hash != self.chain[-1].compute_hash().value:
            logger.error(
                f"Previous hash is not correct {block.previous_hash.hex()} != {self.chain[-1].compute_hash().value.hex()}")
            return False

        # Check if the hash satisfies the difficulty requirements
        block_hash = block.compute_hash()
        if log2(block_hash.value_as_int()) < (
                self.difficulty.hash_len_chars * 8 - self.difficulty.n_bits):
            logger.error(
                "Mined block was not mined with correct difficulty, or not mined properly")
            return False

        if block.diff != self.difficulty:
            logger.error(
                f"Block difficulty is not same, Block: {block.diff} != Blockchain: {self.difficulty}")
            return False

        # Check if the timestamp is greater than the last block's timestamp
        # IDK if this check should be here
        if block.index > 0 and block.timestamp < self.get_last().timestamp:
            logger.error(
                f"Timestamp is traveling back in time {block.timestamp} < {self.get_last().timestamp}")
            return False

        # Check if the hash is not already in the chain
        if block_hash.value in self.chain_hashes:
            logger.error("Hash of block is already in the chain")
            return False

        return True

    def clear(self):
        self.chain.clear()
        self.chain_hashes.clear()

    def insert(self, block: Block):
        if self.validate_next_block(block):
            self.chain.append(block)
            self.chain_hashes.add(block.get_hash())
            self.latency = (datetime.now().timestamp() - block.timestamp) * 1000
            if self.save:
                asyncio.run(self._save_block(block))
            logger.debug(f"Inserted! {block} into {self.name}")
            return True
        logger.error(f"Block {block} validation failed")
        logger.error(f"Blockchain that has failed to insert block \n{self}")
        return False

    def __str__(self):
        out = f"Name: {self.name} | ID: {self.id} | Blockchain Version: {self.version} | Latency: {self.latency} | Blocks:\n"
        for block in self.chain:
            out += f"{block}"
        return out

    def template_next_block(self, requested_diff: Difficulty, data: bytes | bytearray):
        logger.debug(f"Templated next block with difficulty {requested_diff}")
        last = self.get_last()
        return Block(last.index + 1, last.hash, requested_diff, data)

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, value: Difficulty):
        self._difficulty = value
        logger.debug(f"Set new blockchain difficulty {value}")
        block_difficulty_bits.set(value.n_bits)
        block_difficulty_time.set(value.t_cost)
        block_difficulty_memory.set(value.m_cost)
        block_difficulty_parallel.set(value.p_cost)

    async def _save_block(self, block):
        with session_scope() as session:
            bdb = BlockTable(blockchain_id=self._id, index=block.index,
                             hash=block.get_hash(),
                             previous_hash=block.previous_hash, data=block.data,
                             nonce=block.nonce)
            session.add(bdb)
            session.flush()
            if block.signature:
                bst = BlockSignatureTable(block_id=bdb.block_id,
                                          signature=KeyManager.key_to_base64(
                                              block.signature))
                session.add(bst)
            session.commit()

    @property
    def id(self):
        return self._id
