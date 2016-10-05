from __future__ import print_function, unicode_literals, absolute_import
import arcpy

"""ArcGIS Pro project related utilities"""

class AprxObj(object):
    """ turn an aprx path into an aprx object
    attributes:
        path: a string representing an aprx file
    """
    def __init__(self, aprx_path):
        """ :return reference to aprx"""
        self.aprx = arcpy.mp.ArcGISProject(aprx_path)

    def get_map_object(self):
        """ :return map object"""
        m = self.aprx.listMaps()[0]
        return m

    def get_layer_obj_as_array(self):
        """ :return array of layer objects"""
        layer_obj_array = []
        lyr_list = self.get_map_object()
        for layer in lyr_list.listLayers():
            layer_obj_array.append(layer)
        return layer_obj_array

    def get_layer_obj_gen(self):
        """ yields layer objects"""
        lyr_list = self.get_map_object()
        for layer in lyr_list.listLayers():
            yield layer

    def get_layer_names_as_array(self):
        """ :return array of layer names"""
        lyr_name_array = []
        for lyr in self.get_layer_obj_as_array():
            lyr_name_array.append(lyr.name)
        return lyr_name_array

    def get_layer_names_gen(self):
        """ yields layer names"""
        for lyr in self.get_layer_names_as_array():
            yield lyr