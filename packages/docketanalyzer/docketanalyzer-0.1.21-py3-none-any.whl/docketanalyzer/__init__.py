from docketanalyzer.config import EnvConfig, ConfigKey
import docketanalyzer.utils as utils
from docketanalyzer.tools.registry import Registry

import docketanalyzer.choices as choices
from docketanalyzer.tools.s3 import S3Utility
from docketanalyzer.tools.websearch import WebSearch

from docketanalyzer.cli import cli

extensions = {
    'core': dict(
        names=[
            'CoreDataset', 'load_dataset',
            'DocketBatch', 'DocketIndex', 'load_docket_index', 'DocketManager',
            'load_elastic', 'JuriscraperUtility',
            'Task', 'DocketTask', 'task_registry', 'register_task', 'load_tasks', 'load_task',
        ],
    ),
    'pipelines': dict(
        names=[
            'parallel_inference', 
            'Pipeline', 'pipeline', 'remote_pipeline',
            'Routine', 'training_routine',
        ],
    ),
}


from docketanalyzer.utils import lazy_load

__all__ = ['EnvConfig', 'ConfigKey', 'utils', 'Registry', 'choices']

for extension_name, extension in extensions.items():
    names = extension['names']
    module = f"docketanalyzer_{extension_name}"
    for name in extension['names']:
        globals()[name] = lazy_load(module, name, extension_name)
        __all__.append(name)
