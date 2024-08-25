import click

from decentnet.cli.client import client
from decentnet.cli.keys import key
from decentnet.cli.service import service
from decentnet.modules.logger.log import setup_logger


@click.group()
def cli():
    pass


cli.add_command(key)
cli.add_command(service)
cli.add_command(client)

if __name__ == '__main__':
    setup_logger(True)
    cli()


def main():
    setup_logger(True)
    cli()
