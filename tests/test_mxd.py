from arc_utils import mxd


def test_mxdobj_properties(testmxd):
    mxdpath = testmxd
    mxdobj = mxd.MxdObj(mxdpath)
    assert mxdobj.path == mxdpath
    #assert mxdobj.mxd is object
    assert mxdobj.layer_names_array == [u'test_fc']
    assert isinstance(mxdobj.layer_obj_array, list)

