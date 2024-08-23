import click
from .dev import dev_cli
from .configure import configure
from .hello import hello


@click.group()
def cli():
    pass


cli.add_command(dev_cli)
cli.add_command(configure)
cli.add_command(hello)
