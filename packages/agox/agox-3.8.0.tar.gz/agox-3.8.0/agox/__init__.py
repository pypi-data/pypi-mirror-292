import os

# Versioning
__version_info__ = (3, 8, 0)
__version__ = '{}.{}.{}'.format(*__version_info__)

# Extra versioning - Mainly for managing Pypi releases.
version_extra = os.environ.get('AGOX_VERSION_EXTRA', None)
if version_extra:
    __version__ = '{}{}'.format(__version__, version_extra)

try: # When installing the package we don't need to actually import.
    from agox.module import Module
    from agox.observer import Observer
    from agox.writer import Writer
    from agox.tracker import Tracker
    from agox.main import AGOX

    __all__ = ['Module', 'Observer', 'Writer', 'Tracker', 'AGOX', '__version__']

except ImportError:
    pass



