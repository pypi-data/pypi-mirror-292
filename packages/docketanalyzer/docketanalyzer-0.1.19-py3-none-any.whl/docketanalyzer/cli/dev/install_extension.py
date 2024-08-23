import os
import site
import sys
import click
from pathlib import Path
import simplejson as json


def create_egg_link(package_name, package_path):
    site_packages = site.getsitepackages()[0]
    egg_link_path = os.path.join(site_packages, f"{package_name}.egg-link")
    with open(egg_link_path, "w") as f:
        f.write(str(package_path))
        f.write("\n.")


def update_easy_install_pth(package_path):
    site_packages = site.getsitepackages()[0]
    easy_install_path = os.path.join(site_packages, "easy-install.pth")
    with open(easy_install_path, "a+") as f:
        f.seek(0)
        content = f.read()
        if str(package_path) not in content:
            f.write(f"\n{package_path}\n")


def create_pth_file(package_name, src_path):
    site_packages = site.getsitepackages()[0]
    pth_path = os.path.join(site_packages, f"{package_name}.pth")
    print(pth_path)
    with open(pth_path, "w") as f:
        f.write(str(src_path))


@click.command()
def install_extension():
    """
    Perform an editable installation of the package.
    """
    base_dir = Path.cwd()
    src_dir = base_dir / 'src'

    config_path = base_dir / 'build_config.json'
    build_config = json.loads(config_path.read_text())
    package_name = build_config['package_name']

    create_egg_link(package_name, base_dir)
    update_easy_install_pth(base_dir)
    create_pth_file(package_name, src_dir)

    sys.path.insert(0, str(src_dir))

    click.echo(f"Extension {package_name} installed.")
