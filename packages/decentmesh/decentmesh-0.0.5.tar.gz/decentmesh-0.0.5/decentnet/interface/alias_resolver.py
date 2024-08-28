from typing import Optional, Tuple

from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import OwnedKeys


class AliasResolver:
    """
    AliasResolver is responsible for resolving the public key and key ID based on a given alias.
    """

    @classmethod
    def get_key_by_alias(cls, alias: str) -> Optional[Tuple[str, int]]:
        """
        Retrieves the public key and key ID based on the given alias.

        Args:
            alias (str): The alias to search for

        Returns:
            Optional[Tuple[str, int]]: A tuple containing the public key and key ID if found, otherwise None.
        """
        with session_scope() as session:
            key = session.query(OwnedKeys).filter_by(alias=alias).first()
            if key:
                return key.public_key, key.id
            return None
