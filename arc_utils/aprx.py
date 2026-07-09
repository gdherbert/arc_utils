# -*- coding: utf-8 -*-
"""ArcGIS Pro aprx related utilities
"""

import arcpy
import os
from ._inputs import resolve_aprx_path

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
        self.path = resolve_aprx_path(aprx_path, arg_name="aprx_path")
        if self.path != "CURRENT" and not os.path.exists(self.path):
            raise ValueError("invalid path")
        self.aprx = arcpy.mp.ArcGISProject(self.path)
        self.maps = self.get_maps()
        self.layouts = self.get_layouts()
        
    def get_maps(self):
        """ :return array of map objects"""
        map_array = []
        for map in self.aprx.listMaps():
            map_array.append(map)
        return map_array

    def get_layouts(self):
        """ :return array of layout objects"""
        layout_array = []
        for layout in self.aprx.listLayouts():
            layout_array.append(layout)
        return layout_array

    def get_layer_obj_as_array(self, map):
        """ :param: map object
        :return array of layer objects in a specified map object"""
        layer_obj_array = []
        for layer in map.listLayers():
            layer_obj_array.append(layer)
        return layer_obj_array

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

