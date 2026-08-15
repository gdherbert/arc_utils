"""A collection of python utilities for ArcGIS Pro
"""
from importlib.metadata import PackageNotFoundError, version

try:
	__version__ = version('arc-utils')
except PackageNotFoundError:
	__version__ = '0+unknown'

__author__ = 'Grant Herbert'

__all__ = ['aprx.py', 'gdb.py', 'table.py']

from arc_utils import gdb
from arc_utils import table
from arc_utils import aprx