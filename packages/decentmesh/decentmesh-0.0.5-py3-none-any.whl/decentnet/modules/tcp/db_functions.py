import logging

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import NodeInfoTable, AliveBeam
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


def remove_alive_beam_from_db(host: str, port: int):
    with session_scope() as session:
        node_info = session.query(NodeInfoTable).where(
            (
                    NodeInfoTable.ipv4 == host or NodeInfoTable.ipv6) == host and NodeInfoTable.port == port).first()
        if node_info:
            pub_key_base64 = node_info.pub_key
            logger.debug(f"Removing dead beam {pub_key_base64}")
            ab = session.query(AliveBeam).where(
                AliveBeam.pub_key == pub_key_base64).first()
            if ab:
                session.delete(ab)
                session.commit()


async def remove_alive_beam_from_db_w_pub_key(pub_key_base64: str):
    if not pub_key_base64:
        return
    with session_scope() as session:
        logger.debug(f"Removing dead beam {pub_key_base64}")
        ab = session.query(AliveBeam).where(AliveBeam.pub_key == pub_key_base64).first()
        if ab:
            session.delete(ab)
            session.commit()
