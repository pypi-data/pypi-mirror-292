from dbt_column_lineage.main import main

try:
    from ._version import version as __version__
except ImportError:
    import warnings
    warnings.warn('Failed to read version. Make sure `setuptools_scm` is installed and its setup is called.')
    __version__ = '0.0.0'

__all__ = ['__version__']