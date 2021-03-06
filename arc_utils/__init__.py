"""A collection of python utilities for ArcGIS Desktop and ArcGIS Pro
"""
__version__ = '0.7'
__author__ = 'Grant Herbert'

__all__ = ['gdb.py', 'table.py']

import sys
if sys.version_info.major == 3:
    raise Exception("This version of arc_utils only supports Python 2.7")
else:
    from arc_utils import gdb
    from arc_utils import table
    from arc_utils import mxd