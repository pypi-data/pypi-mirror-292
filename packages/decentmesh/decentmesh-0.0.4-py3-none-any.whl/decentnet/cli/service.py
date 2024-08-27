import multiprocessing

import click
import rich

from decentnet.cli.keys import generate_impl
from decentnet.modules.banner.banner import orig_text
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import OwnedKeys, AliveBeam
from decentnet.modules.migrate.migrate_agent import MigrateAgent
from decentnet.modules.monitoring.statistics import Stats
from decentnet.modules.seed_connector.SeedsAgent import SeedsAgent
from decentnet.modules.tcp.server import TCPServer


@click.group()
def service():
    pass


@service.command()
@click.argument('host', type=click.STRING)
@click.argument('port', type=int)
def start(host: str, port: int):
    rich.print(orig_text)
    MigrateAgent.do_migrate()
    multiprocessing.Process(target=Stats.start_prometheus_server).start()
    rich.print("Starting DecentMesh...")
    with session_scope() as session:
        for beam in session.query(AliveBeam).all():
            session.delete(beam)
            session.commit()
        if session.query(OwnedKeys).first() is None:
            rich.print("Generating first keys for communication")
            generate_impl(private_key_file=None, public_key_file=None,
                          description="First Key", sign=True)
            generate_impl(private_key_file=None, public_key_file=None,
                          description="First Key", sign=True)
            generate_impl(private_key_file=None, public_key_file=None,
                          description="First Key", sign=True)
            generate_impl(private_key_file=None, public_key_file=None,
                          description="First Key", sign=False)

    server = TCPServer(host, port)
    server_process = multiprocessing.Process(target=server.run)
    server_process.start()
    rich.print("Connecting to DecentMesh seed nodes...")
    SeedsAgent(host, port)
