# README #


### What is this repository for? ###
* A collection of (mostly) arcpy related utilities for use within ArcGIS Desktop (Python 2.7), or ArcGIS Pro (Python 3) as well where possible.
Shortcuts for accessing elements of a map document, performing various data discovery tasks on a table or gdb

### How do I get set up? ###

* To install the utilities: 
* `pip install arc_utils`
* Clone the repo to your machine and add the path to the python install https://docs.python.org/2/tutorial/modules.html#the-module-search-path
* Optionally, you can copy the folder to the site-packages in the ESRI python install directory, or add a .pth file to the site-packages folder pointing to the clone directory.

To use the utilities:

* in the python window in ArcMap/ArcCatalog/Pro

``import arc_utils as au
``

* typing ``au.`` will now reveal the modules and functions available to you if you have autocomplete on

* Depends on arcpy (only available with Esri license)

### Example usage ###

``import arc_utils as au``

``tbl = au.table.TableObj(path to featureclass)``

# list all fields 

``print(tbl.fields)``

``mxd_doc = au.mxd.MxdObj(“CURRENT”)``

``mxd_doc.layer_names_array`` >> [‘layer1’,’layer2’]

``pro_doc = au.aprx.AprxObj(“CURRENT”)``

``pro_doc.maps`` >> [<arcpy._mp.Map object at 0x000001A4AECBF108>, <arcpy._mp.Map object at 0x000001A4AEBB6608>]

``pro_doc.maps[0].name`` >> ‘Map’

### Contribution guidelines ###

Contributions welcomed, this is a starting point for various utilities that I think could be useful within Arc.
