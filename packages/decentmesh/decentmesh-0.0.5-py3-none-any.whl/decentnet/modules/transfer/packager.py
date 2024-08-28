import logging
from typing import Optional

import cbor2
from ecdsa import SigningKey

from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.blockchain.block import Block
from decentnet.modules.cryptography.asymetric import AsymCrypt
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.serializer.serializer import Serializer

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class Packager:
    @classmethod
    def genesis_package(cls, owner_key_id: int, receiver_key_pub_key: str,
                        block: Block):
        raise NotImplementedError()

    @classmethod
    def check_verified(cls, data: dict, verified: bool):
        """
        If verified is False, this will raise an exception with log
        :param data: Data of block for logging
        :param verified:
        """
        if not verified:
            logger.error(f"Invalid signature, failed to verify data: {data}")
            raise Exception("Invalid signature")

    @classmethod
    def pack(cls, owner_key_id: int, block: Block,
             target_pub_key: Optional[str]) -> bytes:
        o_priv_key, o_pub_key = KeyManager.retrieve_ssh_key_pair_from_db(owner_key_id)
        block_bytes = block.to_bytes()
        signature = cls.sign_block(owner_key_id, block_bytes)

        data = Serializer.serialize_data(
            o_pub_key, signature,
            block_bytes, target_pub_key)
        logger.debug(f"Packed data into {cbor2.loads(data)}")
        return data

    @classmethod
    def sign_block(cls, owner_key_id: int, block_bytes: bytes):
        o_priv_key, _ = KeyManager.retrieve_ssh_key_pair_from_db(owner_key_id)
        block_bytes = block_bytes
        return AsymCrypt.sign_message(private_key=o_priv_key, data=block_bytes)

    @classmethod
    def add_cmd(cls, unpacked_request: dict, owner_key_id: int, cmd: int) -> dict:
        """
        Adding cmd key to dict
        :param unpacked_request:
        :param owner_key_id:
        :param cmd: This is an int from CMD enum
        :return: Data with added cmd in dictionary
        """
        cpy_unpacked = dict(unpacked_request)
        o_priv_key, o_pub_key = KeyManager.retrieve_ssh_key_pair_from_db(owner_key_id)
        cmd_bytes = cmd.to_bytes(2, byteorder=ENDIAN_TYPE, signed=False)
        signature = AsymCrypt.sign_message(private_key=o_priv_key, data=cmd_bytes)

        cpy_unpacked["cmd"] = cmd
        cpy_unpacked["csig"] = signature
        cpy_unpacked["cpub"] = o_pub_key
        logger.debug(
            f"Added cmd and raw supporting values to packed result: {cpy_unpacked}")
        return cpy_unpacked

    @classmethod
    def unpack(cls, serialized_data: bytes) -> tuple[bool, dict, Optional[bool]]:
        """
        Unpacks and verifies block
        :param serialized_data:
        :return: verified and data

        keys:
        "pub"
        "sig"
        "data"
        "target"
        """
        data = Serializer.deserialize_data(serialized_data)
        decoded_pub_key = AsymCrypt.verifying_key_from_string(data["pub"])
        verified = AsymCrypt.verify_signature(
            public_key=decoded_pub_key,
            data=data["data"], signature=data["sig"])
        if "cmd" in data.keys():
            decoded_cpub_key = AsymCrypt.verifying_key_from_string(data["cpub"])
            verified_csig = Packager.verify_csig(data, decoded_cpub_key)
        else:
            verified_csig = None
        return verified, data, verified_csig

    @classmethod
    def verify_csig(cls, data, decoded_cpub_key):
        return AsymCrypt.verify_signature(
            public_key=decoded_cpub_key,
            data=data["cmd"].to_bytes(2, byteorder=ENDIAN_TYPE, signed=False),
            signature=data["csig"])

    @classmethod
    def sign_dict_data(cls, private_key: SigningKey, attribute: str, data: dict):
        """
        This will add signature to data attribute
        :param private_key:
        :param attribute:
        :param data:
        """
        signature = AsymCrypt.sign_message(private_key, data[attribute].encode("ascii"))
        data["sig"] = signature
        return data

    @classmethod
    def verify_dict_data(cls, public_key: str, attribute: str, data: dict):
        """
        Verifies data from a key in dict
        :param public_key:
        :param attribute:
        :param data:
        :return:
        """
        pub_key_raw = AsymCrypt.public_key_from_base64(public_key, False)
        return AsymCrypt.verify_signature(public_key=pub_key_raw, signature=data["sig"],
                                          data=data[attribute].encode("ascii"))
