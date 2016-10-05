from __future__ import print_function, unicode_literals, absolute_import
"""ArcGIS Desktop mxd related utilities
"""

import arcpy

class MxdObj(object):
    """ provide methods for working with a Arc Desktop mxd file
    attributes:
        path: a string representing an mxd file
    """
    def __init__(self, mxd_path):
        """ sets up reference to mxd
        adds methods
        """
        self.mxd = arcpy.mapping.MapDocument(mxd_path)
        self.layer_obj_array = self.get_layer_obj_as_array()
        self.layer_names_array = self.get_layer_names_as_array()

    def get_layer_obj_as_array(self):
        """ :return array of layer objects"""
        layer_obj_array = []
        for layer in arcpy.mapping.ListLayers(self.mxd):
            layer_obj_array.append(layer)
        return layer_obj_array

    def get_layer_obj_gen(self):
        """ yields layer objects"""
        for layer in arcpy.mapping.ListLayers(self.mxd):
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


def mxd_from_path(mxd_path):
    """ :returns mxd object
    """
    mxd = arcpy.mapping.MapDocument(mxd_path)
    return mxd

def list_layers_in_mxd(mxd):
    """ :returns array of layer objects
    """
    layer_list = []
    for layer in arcpy.mapping.ListLayers(mxd):
        layer_list.append(layer)
    return layer_list
