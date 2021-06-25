"""A collection of python utilities for ArcGIS Desktop and ArcGIS Pro
"""
__version__ = '1.0'
__author__ = 'Grant Herbert'

__all__ = ['gdb.py', 'table.py']

import sys
if sys.version_info.major == 3:
    from arc_utils import gdb
    from arc_utils import table
    from arc_utils import aprx
else:
    from arc_utils import gdb
    from arc_utils import table
    from arc_utils import mxd