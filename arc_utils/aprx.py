# -*- coding: utf-8 -*-
"""ArcGIS Pro aprx related utilities
"""

import arcpy
from ._inputs import _ensure_valid_path
from ._inputs import _resolve_aprx_path

class AprxObj(object):
    """ provide methods for working with a ArcGIS Pro aprx file
    all standard arcpy methods are available via .aprx
    Usage: pro_doc = arc_utils.aprx.AprxObj(path)
    :param
        path: aprx input accepted as
            - string path
            - pathlib.Path / os.PathLike
            - wrapper object exposing .path
            - "CURRENT" if used in ArcGIS Pro Python window
        invalid paths raise ValueError("invalid path")
    """
    def __init__(self, aprx_path):
        """ :param path to aprx or "CURRENT"
        """
        self.path = _resolve_aprx_path(aprx_path, arg_name="aprx_path")
        if self.path != "CURRENT":
            self.path = _ensure_valid_path(self.path)
        self.aprx = arcpy.mp.ArcGISProject(self.path)
        self.maps = self.get_maps()
        self.layouts = self.get_layouts()
        
    def get_maps(self):
        """Return maps keyed by stable ArcGIS Pro URI."""
        map_dict = {}
        self.maps_by_name = {}
        for index, map_obj in enumerate(self.aprx.listMaps()):
            map_id = getattr(map_obj, "URI", None) or "map:{}".format(index)
            entry = {
                "name": map_obj.name,
                "map": map_obj,
                "layers": self.get_layer_obj_as_dict(map_obj)
            }
            map_dict[map_id] = entry
            self.maps_by_name.setdefault(map_obj.name, []).append(entry)
        return map_dict

    def get_maps_by_name(self, name):
        """Return all map entries with the requested name."""
        return self.maps_by_name.get(name, [])

    def get_layouts(self):
        """Return layouts keyed by stable ArcGIS Pro URI."""
        layout_dict = {}
        self.layouts_by_name = {}
        for index, layout_obj in enumerate(self.aprx.listLayouts()):
            layout_id = getattr(layout_obj, "URI", None) or "layout:{}".format(index)
            entry = {
                "name": layout_obj.name,
                "layout": layout_obj
            }
            layout_dict[layout_id] = entry
            self.layouts_by_name.setdefault(layout_obj.name, []).append(entry)
        return layout_dict

    def get_layouts_by_name(self, name):
        """Return all layout entries with the requested name."""
        return self.layouts_by_name.get(name, [])

    def get_layer_obj_as_dict(self, map):
        """ :param: map object
        :return dict of layer objects in a specified map object"""
        layer_obj_dict = {}
        for layer in map.listLayers():
            layer_obj_dict[layer.name] = layer
        return layer_obj_dict

    def get_layer_names_as_array(self, map):
        """ :param: map object
        :return array of layer names in a specified map object"""
        lyr_name_array = []
        for layer in map.listLayers():
            lyr_name_array.append(layer.name)
        return lyr_name_array

    def layer_obj_generator(self, map):
        """ :param: map object
        yields layer objects"""
        for layer in map.listLayers():
            yield layer

    def layer_names_generator(self, map):
        """ :param: map object
        yields layer names"""
        for layer in map.listLayers():
            yield layer.name


# instantiated on import so `arc_utils.aprx.current` is ready with autocomplete
# (.maps, .layouts, etc.) in the ArcGIS Pro Python window; None outside Pro
try:
    current = AprxObj("CURRENT")
except (arcpy.ExecuteError, OSError):
    current = None
