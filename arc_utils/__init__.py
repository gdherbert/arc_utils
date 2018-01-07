"""A collection of python utilities for ArcGIS Desktop and ArcGIS Pro
"""
__version__ = '0.6'
__author__ = 'Grant Herbert'

__all__ = ['gdb.py', 'table.py']

import sys
from arc_utils import gdb
from arc_utils import table
if sys.version_info.major == 3:
    from arc_utils import aprx
else:
    from arc_utils import mxd