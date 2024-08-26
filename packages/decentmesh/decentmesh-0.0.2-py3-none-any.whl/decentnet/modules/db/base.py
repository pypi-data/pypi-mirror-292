import logging
import os
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import DB_FILENAME, DATABASE_URL
from decentnet.modules.db.models import Base
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


@lru_cache()
def get_root_dir() -> Path:
    return Path(os.path.abspath(__file__)).parent.parent.parent.parent


db_file = get_root_dir() / DB_FILENAME
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_recycle=3600)
Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
