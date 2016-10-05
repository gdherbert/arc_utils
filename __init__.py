"""ArcGIS python utilities"""
__VERSION__ = '0.5'
__AUTHOR__ = 'Grant Herbert'

__all__ = ['fieldutils', 'gdbutils', 'tableutils']

import sys
from arcutils import fieldutils
from arcutils import gdbutils
from arcutils import tableutils
if sys.version_info.major == 3:
    from arcutils import aprxutils
else:
    from arcutils import mxdutils
