# -*- coding: utf-8 -*-
"""ArcGIS Pro aprx related utilities
"""

import arcpy

class AprxObj(object):
    """ provide methods for working with a ArcGIS Pro aprx file
    all standard arcpy methods are available via .aprx
    Usage: pro_doc = arc_utils.aprx.AprxObj(path)
    :param
        path: a string representing an aprx file, 
        or "CURRENT" if used in ArcGIS Pro Python window
    """
    def __init__(self, aprx_path):
        """ :param path to aprx or "CURRENT"
        """
        self.aprx = arcpy.mp.ArcGISProject(aprx_path)
        self.path = aprx_path
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

