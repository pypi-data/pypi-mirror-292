"""
Debug Constants
"""
import logging
import os

RUN_IN_DEBUG = bool(os.getenv("DEBUG", True))
LOG_LEVEL = os.getenv("DEBUG_LEVEL", logging.DEBUG)
ENCRYPTION_DEBUG = bool(os.getenv("ENCRYPTION_DEBUG", False))

SEEDS_AGENT_LOG_LEVEL = os.getenv("SEEDS_AGENT_LOG_LEVEL", logging.INFO)
COMPRESSION_LOG_LEVEL = os.getenv("COMPRESSION_LOG_LEVEL", logging.INFO)
R2R_LOG_LEVEL = os.getenv("R2R_LOG_LEVEL", logging.INFO)
