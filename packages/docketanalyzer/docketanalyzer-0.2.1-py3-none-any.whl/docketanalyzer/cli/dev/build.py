import os
import shutil
import click
import docketanalyzer
from docketanalyzer import PYPI_TOKEN, package_data
from .build_extension import update_version


@click.command()
@click.option('--push', is_flag=True, help="Push to PyPI after building")
def build(push):
    """
    Build and / or push docketanalyzer.
    """
    extensions_data = package_data('extensions')
    package_dir = extensions_data.path.parents[2]
    extension_names = [
        x.name.replace('docketanalyzer_', '') 
        for x in (package_dir / 'extensions').glob('*') 
        if x.is_dir() and x.name.startswith('docketanalyzer_')
        and not x.name.endswith('.egg-info')
    ]
    extensions_data.path.write_text('\n'.join(extension_names))

    build_dir = package_dir / 'build'
    dist_dir = package_dir / 'dist'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    setup_path = package_dir / 'setup.py'
    version = update_version(docketanalyzer.__version__)
    version_path = package_dir / 'docketanalyzer' / '_version.py'
    version_path.write_text(f'__version__ = "{version}"\n')

    cmd = f"cd {package_dir} && python {setup_path} bdist_wheel --dist-dir={dist_dir}"
    os.system(cmd)
    
    if push:
        cmd = f"pip install -e {package_dir}"
        os.system(cmd)

        cmd = f"twine upload {dist_dir}/*"
        if PYPI_TOKEN is not None:
            cmd += f" -u __token__ -p {PYPI_TOKEN}"
        os.system(cmd)
    
        shutil.rmtree(build_dir)
        shutil.rmtree(dist_dir)
