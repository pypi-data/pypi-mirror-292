# read version from installed package
from importlib.metadata import version
from . import load_data

__version__ = version("iddn")
