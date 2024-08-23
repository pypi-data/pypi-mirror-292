import os
from setuptools import setup
import shutil
import sys
import click
from pathlib import Path
import simplejson as json
from docketanalyzer.utils import PYPI_TOKEN


def parse_version(version_str):
    return tuple(map(int, version_str.split('.')))


def is_valid_increment(v1, v2):
    if v1 == v2:
        return True, "Versions are identical"
    
    for i in range(3):
        if v2[i] > v1[i]:
            if v2[i] == v1[i] + 1 and v2[i+1:] == (0,) * (2-i):
                return True, f"Valid increment at {'major' if i == 0 else 'minor' if i == 1 else 'patch'} level"
            else:
                return False, "Invalid increment"
        elif v2[i] < v1[i]:
            return False, "Second version is lower"
    
    return False, "Other issue"


def compare_versions(version1, version2):
    v1 = parse_version(version1)
    v2 = parse_version(version2)
    
    result, message = is_valid_increment(v1, v2)
    return result, message


def update_version(version):
    while 1:
        new_version = input(f"Current version is {version}. Enter new version or leave blank to keep: ")
        if not new_version:
            new_version = version
        result, message = compare_versions(version, new_version)
        if result:
            break
        print('Invalid version change:', message)
    return new_version


@click.command()
@click.option('--push', is_flag=True, help="Push to PyPI after building")
def build(push):
    """
    Build package from build_config.json
    """
    base_dir = Path.cwd()

    build_dir = base_dir / 'build'
    dist_dir = base_dir / 'dist'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    config_path = base_dir / 'build_config.json'
    build_config = json.loads(config_path.read_text())
    build_config['version'] = update_version(build_config['version'])
    config_path.write_text(json.dumps(build_config, indent=2))

    sys.argv = [sys.argv[0], 'bdist_wheel']

    setup(
        name=build_config['name'],
        version=build_config['version'],
        description=build_config.get('description'),
        url=build_config.get('url'),
        author=build_config.get('author'),
        packages=[build_config['package_name']],
        include_package_data=build_config.get('include_package_data', False),
        install_requires=build_config['install_requires'],
        entry_points=build_config.get('entry_points', {}),
    )

    if push:
        cmd = f"twine upload {dist_dir}/*"
        if PYPI_TOKEN is not None:
            cmd += f" -u __token__ -p {PYPI_TOKEN}"
        os.system(cmd)
