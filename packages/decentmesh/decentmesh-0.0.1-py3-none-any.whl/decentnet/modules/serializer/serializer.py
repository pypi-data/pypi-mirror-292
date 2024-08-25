import logging
from typing import Optional

import cbor2
from _cbor2 import CBORDecodeValueError
from ecdsa import VerifyingKey

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.cryptography.asymetric import AsymCrypt
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class Serializer:
    @staticmethod
    def serialize_data(public_key: VerifyingKey | str, signature: bytes,
                       encrypted_data: bytes,
                       target_pub_key: Optional[str] = None, cmd: Optional[int] = None,
                       command_signature: Optional[bytes] = None,
                       command_public_key=Optional[VerifyingKey]) -> bytes:
        """Serializes public key, signature,
        and encrypted data and returns them as separate bytes.

        :returns: utf-8 encoded json
        """

        out = {"pub": public_key if type(
            public_key) is str else AsymCrypt.verifying_key_to_string(public_key),
               "sig": signature,
               "data": encrypted_data,
               "target": target_pub_key}
        if cmd and command_signature:
            out["cmd"] = cmd
            out["csig"] = command_signature
            out["cpub"] = AsymCrypt.verifying_key_to_string(command_public_key)
        return cbor2.dumps(out)

    @staticmethod
    def deserialize_data(serialized_data: bytes) -> dict:
        """Deserializes the provided data and returns the public key, signature, and encrypted data."""
        try:
            deserialized_data = cbor2.loads(serialized_data)
        except (
                cbor2.CBORDecodeError, cbor2.CBORDecodeValueError,
                CBORDecodeValueError) as e:
            logger.error(f"Failed to decode cbor {serialized_data}")
            raise e
        try:
            if "sig" not in deserialized_data.keys():
                raise Exception(f"Corrupted data {deserialized_data}")
        except AttributeError as ex:
            raise Exception(f"Invalid data deserialized {ex}, data {deserialized_data}")

        return deserialized_data
