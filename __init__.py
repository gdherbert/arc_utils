"""A collection of python utilities for ArcGIS Desktop and ArcGIS Pro
"""
__version__ = '0.6'
__author__ = 'Grant Herbert'

__all__ = ['gdb.py', 'table.py']

import sys
from arcutils import gdb
from arcutils import table
if sys.version_info.major == 3:
    from arcutils import aprx
else:
    from arcutils import mxd
