# README #


### What is this repository for? ###
* A collection of (mostly) arcpy related utilities for use within ArcGIS Pro (Python 3).
Shortcuts for accessing elements of a map document, performing various data discovery tasks on a table or geodatabase

### How do I get set up? ###

Install from PyPI:

```bash
pip install arc-utils
```

For local development and editable usage from clone:

```bash
python -m pip install -e .
```

To use the utilities:

* in the python window in ArcGIS Pro

``import arc_utils as au``

* typing ``au.`` will now reveal the modules and functions available to you if you have autocomplete on

* Depends on arcpy (only available with Esri license)

### Example usage ###

``import arc_utils as au``

``tbl = au.table.TableObj(path to featureclass)``

# list all fields 

``print(tbl.fields)``

``pro_doc = au.aprx.AprxObj(“CURRENT”)``

``pro_doc.maps`` >> [<arcpy._mp.Map object at 0x000001A4AECBF108>, <arcpy._mp.Map object at 0x000001A4AEBB6608>]

``pro_doc.maps[0].name`` >> ‘Map’

### Accepted Input Types ###

Most path parameters now accept:

* string path
* ``pathlib.Path`` / other path-like objects
* wrapper objects with ``.path``
* ArcGIS layer/table objects with ``.catalogPath`` or ``.dataSource`` (where applicable)

Invalid paths raise ``ValueError("invalid path")``.

Constructor acceptance is preserved (for example, passing path-like and wrapper objects directly to ``TableObj``, ``GDBObj``, and ``AprxObj``).

### Exporting field values to Excel ###

```python
import arc_utils as au
from openpyxl import Workbook

# Single table export with class method
tbl = au.table.TableObj(r"C:\path\to\featureclass")
wb = Workbook()
ws = wb.active
tbl.export_fields_to_worksheet(ws)
wb.save(r"C:\path\to\schema_values.xlsx")
```

```python
# Multi-layer export with module function
layers = [r"C:\path\to\layer1", r"C:\path\to\layer2"]
au.table.export_field_sets(layers, r"C:\path\to\all_layers.xlsx")
```

```python
# Worksheet naming behavior:
# use_lyr_alias=True -> prefer alias/name (human-readable)
# use_lyr_alias=False -> use full table path (traceable)
au.table.export_field_sets(layers, r"C:\path\to\all_layers.xlsx", use_lyr_alias=True)
au.table.export_field_sets(layers, r"C:\path\to\all_layers_by_path.xlsx", use_lyr_alias=False)
```

```python
# Duplicate detection outputs
tbl = au.table.TableObj(r"C:\path\to\featureclass")
dup_values = tbl.find_duplicate_field_values("STATUS", output="set")
dup_rows_df = tbl.find_duplicate_field_values(["STATUS", "TYPE"], output="df")
```

### Contribution guidelines ###

Contributions welcomed, this is a starting point for various utilities that I think could be useful within ArcGIS Pro.
