import os
from pathlib import Path

from prometheus_client import CollectorRegistry

# Local tasks config
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL", 0)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")  # Default Redis port is 6379
PROMETHEUS_HOST = os.getenv("PROMETHEUS_HOST", "localhost")
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8135"))

registry = CollectorRegistry()
os.environ["prometheus_multiproc_dir"] = str(Path(__file__).parent.parent.parent / "tmp/prometheus")
if not os.path.exists(os.environ["prometheus_multiproc_dir"]):
    os.makedirs(os.environ["prometheus_multiproc_dir"])

# DB config
# If using sqlite
DB_FILENAME = os.getenv("DB_FILENAME", "main.db")

# If using mysql, this needs to be specified
DB_USER = os.getenv("DB_USER", None)
DB_PASSWORD = os.getenv("DB_PASSWORD", None)
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", None)
DB_NAME = os.getenv("DB_NAME", None)

# Construct the connection string
if DB_USER and DB_PASSWORD and DB_HOST and DB_PORT and DB_NAME:
    DATABASE_URL = os.getenv("DATABASE_URL",
                             f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
else:
    DATABASE_URL = f"sqlite:///{DB_FILENAME}"
