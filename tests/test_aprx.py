import sys
if sys.version_info.major == 3:
    from arc_utils import aprx

    def test_aprxobj_properties(testaprx):
        aprxobj = aprx.AprxObj(testaprx)
        assert aprxobj.path == testaprx
        assert aprxobj.maps[0].name == 'Map'
        assert aprxobj.layouts[0].name == 'MyLayout'
        

    def test_aprxobj_layer_names(testaprx):
        aprxobj = aprx.AprxObj(testaprx)
        assert aprxobj.get_layer_names_as_array(aprxobj.maps[0]) == ['test_fc', 'Topographic']


    def test_aprxobj_layer_obj(testaprx):
        aprxobj = aprx.AprxObj(testaprx)
        map_layer_obj = aprxobj.get_layer_obj_as_array(aprxobj.maps[0])
        assert isinstance(map_layer_obj, list)
        assert map_layer_obj[0].name == 'test_fc'
        

