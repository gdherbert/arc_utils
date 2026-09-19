import sys
if sys.version_info.major == 3:
    from arc_utils import aprx
    import pathlib

    class PathWrapper(object):
        def __init__(self, path):
            self.path = path

    def test_aprxobj_properties(testaprx):
        aprxobj = aprx.AprxObj(testaprx)
        assert aprxobj.path == testaprx
        map_entry = aprxobj.get_maps_by_name('Map')[0]
        assert map_entry['map'].name == 'Map'
        layout_entry = aprxobj.get_layouts_by_name('MyLayout')[0]
        assert layout_entry['layout'].name == 'MyLayout'

    def test_aprxobj_preserves_duplicate_map_names():
        class FakeMap(object):
            def __init__(self, uri, name):
                self.URI = uri
                self.name = name

            def listLayers(self):
                return []

        class FakeProject(object):
            def listMaps(self):
                return [FakeMap('map-1', 'Map'), FakeMap('map-2', 'Map')]

        aprxobj = object.__new__(aprx.AprxObj)
        aprxobj.aprx = FakeProject()
        maps = aprxobj.get_maps()

        assert set(maps.keys()) == set(['map-1', 'map-2'])
        assert len(aprxobj.get_maps_by_name('Map')) == 2
        assert aprxobj.get_maps_by_name('Map')[0]['map'].URI == 'map-1'
        assert aprxobj.get_maps_by_name('Map')[1]['map'].URI == 'map-2'

    def test_aprxobj_preserves_duplicate_layout_names():
        class FakeLayout(object):
            def __init__(self, uri, name):
                self.URI = uri
                self.name = name

        class FakeProject(object):
            def listLayouts(self):
                return [FakeLayout('layout-1', 'Layout'), FakeLayout('layout-2', 'Layout')]

        aprxobj = object.__new__(aprx.AprxObj)
        aprxobj.aprx = FakeProject()
        layouts = aprxobj.get_layouts()

        assert set(layouts.keys()) == set(['layout-1', 'layout-2'])
        assert len(aprxobj.get_layouts_by_name('Layout')) == 2
        assert aprxobj.get_layouts_by_name('Layout')[0]['layout'].URI == 'layout-1'
        assert aprxobj.get_layouts_by_name('Layout')[1]['layout'].URI == 'layout-2'
        

    def test_aprxobj_layer_names(testaprx):
        aprxobj = aprx.AprxObj(testaprx)
        map_obj = aprxobj.get_maps_by_name('Map')[0]['map']
        assert aprxobj.get_layer_names_as_array(map_obj) == ['test_fc', 'Topographic']


    def test_aprxobj_layer_obj(testaprx):
        aprxobj = aprx.AprxObj(testaprx)
        map_obj = aprxobj.get_maps_by_name('Map')[0]['map']
        map_layer_obj = aprxobj.get_layer_obj_as_dict(map_obj)
        assert isinstance(map_layer_obj, dict)
        assert map_layer_obj['test_fc'].name == 'test_fc'


    def test_aprxobj_accepts_pathlike_and_wrapper_inputs(testaprx):
        aprxobj_pathlike = aprx.AprxObj(pathlib.Path(testaprx))
        aprxobj_wrapper = aprx.AprxObj(PathWrapper(testaprx))
        assert aprxobj_pathlike.get_maps_by_name('Map')[0]['map'].name == 'Map'
        assert aprxobj_wrapper.get_layouts_by_name('MyLayout')[0]['layout'].name == 'MyLayout'
        

