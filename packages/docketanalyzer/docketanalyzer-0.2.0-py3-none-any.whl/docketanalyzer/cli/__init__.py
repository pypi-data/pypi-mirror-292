import click
from .dev import dev_cli
from .configure import configure
from .check_docket_dirs import check_docket_dirs
from .open import open_command
from .sync import push, pull
from .tasks import tasks


@click.group()
def cli():
    pass


cli.add_command(dev_cli)
cli.add_command(configure)
cli.add_command(check_docket_dirs)
cli.add_command(open_command)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(tasks)
