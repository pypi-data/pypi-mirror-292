import click
from .build import build
from .install_extension import install_extension


@click.group('dev')
def dev_cli():
    pass


dev_cli.add_command(build)
dev_cli.add_command(install_extension)
