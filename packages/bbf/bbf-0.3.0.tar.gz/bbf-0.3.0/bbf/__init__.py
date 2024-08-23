"""
"""

import os
from pathlib import Path

import numpy as np

from .filterlib import FilterLib
from .stellarlib import StellarLib
from .snfilterset import SNFilterSet
from .magsys import *
from .bspline import lgram


__version__ = "0.3.0"


__all__ = ['FilterLib', 'StellarLib', 'SpecMagsys', 'SNFilterSet', 'SNMagSys']


def get_cache_dir():
    """return a default location for caching stuff
    """
    import platformdirs

    # environment variable overrides default platformdirs
    cache_dir = os.environ.get('BBF_CACHE_DIR')

    if cache_dir is None:
        cache_dir = Path(platformdirs.user_cache_dir('bbf'))
    else:
        cache_dir = Path(cache_dir)

    if not cache_dir.is_dir():
        if cache_dir.exists():
            raise RuntimeError(f"{cache_dir} not a directory")
        cache_dir.mkdir(parents=True)

    return cache_dir


def get_data_dir():
    """return a default location for storing stuff
    """
    import platformdirs

    # environment variable overrides platformdirs
    data_dir = os.environ.get('BBF_DATA_DIR')

    if data_dir is None:
        data_dir = Path(platformdirs.user_data_dir('bbf'))
    else:
        data_dir = Path(data_dir)

    if not data_dir.is_dir():
        if data_dir.exists():
            raise RuntimeError(f"{data_dir} not a directory")
        data_dir.mkdir(parents=True)

    return data_dir
