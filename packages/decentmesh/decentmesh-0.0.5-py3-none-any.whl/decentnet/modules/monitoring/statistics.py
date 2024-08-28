import logging
from wsgiref.simple_server import make_server

import prometheus_client
from prometheus_client.multiprocess import MultiProcessCollector

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import registry, PROMETHEUS_PORT
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class Stats:
    @staticmethod
    def start_prometheus_server():
        logger.debug("Starting prometheus client...")
        MultiProcessCollector(registry)
        app = prometheus_client.make_wsgi_app(registry=registry)
        httpd = make_server('localhost', PROMETHEUS_PORT, app)
        httpd.serve_forever()
