import os
import site
import sys
import click
from pathlib import Path
import simplejson as json


def create_egg_link(package_name, package_path):
    site_packages = site.getsitepackages()[0]
    egg_link_path = os.path.join(site_packages, f"{package_name}.egg-link")
    print(egg_link_path)
    with open(egg_link_path, "w") as f:
        f.write(str(package_path))
        f.write("\n.")


def update_easy_install_pth(package_path):
    site_packages = site.getsitepackages()[0]
    easy_install_path = os.path.join(site_packages, "easy-install.pth")
    print(easy_install_path)
    with open(easy_install_path, "a+") as f:
        f.seek(0)
        content = f.read()
        if str(package_path) not in content:
            f.write(f"\n{package_path}\n")


@click.command()
@click.argument('extension_name')
def install_extension(extension_name):
    """
    Install extension in editable mode for development.
    """
    package_name = 'docketanalyzer_' + extension_name
    extensions_dir = Path(__file__).parents[3] / 'extensions'

    create_egg_link(package_name, extensions_dir)
    update_easy_install_pth(extensions_dir)

    sys.path.insert(0, str(extensions_dir))

    click.echo(f"{extension_name} extension installed.")
