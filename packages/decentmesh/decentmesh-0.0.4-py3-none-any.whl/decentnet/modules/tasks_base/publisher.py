import logging

import redis

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class RedisPublisher:
    _instance = None  # Class variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisPublisher, cls).__new__(cls)
            # Initialize the instance once
            cls._instance.__init_once__(*args, **kwargs)
        return cls._instance

    def __init_once__(self, host='localhost', port=6379, db=0):
        """
        Initializes the RedisPublisher with connection to the Redis server, ensuring
        that this initialization only happens once.
        """
        try:
            # Attempt to create a Redis client and ping the server
            self.redis_client = redis.Redis(host=host, port=port, db=db)
            self.redis_client.ping()
            connection_info = f"Redis Connection Info:\nHost: {host}\nPort: {port}\nDatabase: {db}"
            logger.debug(connection_info)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logger.error(
                f'Redis client unable to connect, not able to relay beams. Error: {e}')

    def publish_message(self, channel: str, message: bytes):
        """
        Publishes a message to a given channel.
        """
        self.redis_client.publish(channel, message)
