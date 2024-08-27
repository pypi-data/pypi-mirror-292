import logging

from ecdsa import VerifyingKey

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.cryptography.asymetric import AsymCrypt
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import ForeignKeys
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class KeyManagerForeign:
    @classmethod
    async def save_to_db(cls, public_key, description, can_encrypt, host=None, port=None):
        with session_scope() as session:
            existing_record = session.query(ForeignKeys).where(
                ForeignKeys.public_key == public_key).first()

            if not existing_record:
                bdb = ForeignKeys(public_key=public_key,
                                  identity=f"{host}:{port}",
                                  description=description, can_encrypt=can_encrypt)
                session.add(bdb)
                session.commit()
                logger.debug(f"Saved new pubkey {public_key}")

    @classmethod
    def retrieve_ssh_key_pair_from_db(cls, key_id: int) -> VerifyingKey | bytes:
        """Retrieve SSH key pair from the database.

        Args:
            key_id (int): The unique identifier of the SSH key pair to retrieve.

        Returns:
            Tuple[str, str] or Tuple[None, None]: A tuple containing the private key
            and public key retrieved from the database. If the specified key_id is not found,
            it returns (None, None).
        """
        logger.info(f"Retrieved Foreign key {key_id=}")
        with session_scope() as session:
            key_pair = session.get(ForeignKeys, key_id)

            if key_pair:
                return AsymCrypt.public_key_from_base64(key_pair.public_key,
                                                        key_pair.can_encrypt)
            else:
                raise Exception("No Key found")
