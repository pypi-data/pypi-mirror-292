import asyncio
import logging
import os
from time import sleep

import pymysql
import redis
import sqlalchemy
from sqlalchemy.exc import IntegrityError

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import REDIS_PORT, REDIS_HOST
from decentnet.modules.comm.relay import Relay
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import AliveBeam
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class Consumer:
    def __init__(self, relay: Relay):
        # Channel is port of peer
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.relay = relay
        while not self.relay.beam_pub_key:
            sleep(1)

        self.id = self.relay.beam_pub_key
        self.redis_client.ping()
        self.channel_name = self.id  # Channel is used for filtering for each consumer socket
        self.save_to_db(False)

        while not relay.beam.connected:
            logger.debug(f"Consumer waiting for beam {self.id} to connect")
            sleep(0.5)
        asyncio.run(self.mark_ready(True))
        self.start()

    def save_to_db(self, ready: bool):
        with session_scope() as session:
            try:
                csd = AliveBeam(pub_key=self.id, ready=ready)
                session.add(csd)
                session.commit()
                logger.debug(f"Saved alive beam {csd.pub_key}")
            except (
                    IntegrityError, pymysql.err.IntegrityError,
                    sqlalchemy.exc.IntegrityError):
                session.rollback()

    async def mark_ready(self, ready: bool):
        await AliveBeam.mark_beam_ready(self.channel_name, ready)

    def start(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.channel_name)

        logger.info(
            f"Consumer subscribed on channel {self.channel_name} PID: {os.getpid()}")

        for message in pubsub.listen():
            if message['type'] == 'message':
                self.process_message(message['data'])

    def process_message(self, message_data: bytes):
        # TODO: check for sync flag and if so just insert block instead of sending

        logger.debug(
            f"Consumer {self.channel_name} sending message to {self.relay.beam.client.host}:{self.relay.beam.client.port}")
        self.relay.beam.client.send_message(message_data,
                                            ack=False)  # TODO: fix relay to beacon
