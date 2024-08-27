from docketanalyzer._version import __version__
from docketanalyzer.utils import *

import sys
from docketanalyzer.data import choices
sys.modules[f"docketanalyzer.choices"] = choices

modules = {
    'docketanalyzer.core.database': ['Database'],
    'docketanalyzer.core.elastic': ['load_elastic'],
    'docketanalyzer.core.object': ['ObjectIndex', 'ObjectManager', 'ObjectBatch'],
    'docketanalyzer.core.s3': ['S3'],
    'docketanalyzer.core.websearch': ['WebSearch'],
    'docketanalyzer.core.task': ['Task', 'DocketTask', 'load_tasks', 'load_task', 'register_task', 'task_registry'],
    'docketanalyzer.data.docket_index': ['DocketIndex', 'load_docket_index'],
    'docketanalyzer.data.docket_manager': ['DocketManager'],
    'docketanalyzer.data.docket_batch': ['DocketBatch'],
}


extensions = package_data('extensions').load()
extension_modules = {}
available_extensions = []
patches = {}
__all__ = []


for extension in extensions:
    extension_module = f'docketanalyzer_{extension}'
    try:
        names = __import__(extension_module).modules
        names = sum(names.values(), [])
        __all__.extend(names)
        extension_modules[extension_module] = names
        available_extensions.append(extension)
        patches[extension] = __import__(extension_module).patch
    except (ModuleNotFoundError, AttributeError):
        pass


lazy_load_modules(modules, globals())
lazy_load_modules(extension_modules, globals())


from docketanalyzer.config import *
from docketanalyzer.cli import cli


for extension, patch in patches.items():
    try:
        patch(globals())
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error applying patch for {extension}: {e}")


__all__ += [
    'lazy_load_modules',
    'PackageConfig', 'ConfigKey', 'config',
    'utils', 'Registry', 'choices',
    'cli', 'extensions', 'available_extensions',
]
