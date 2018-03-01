from arc_utils import mxd

mxdpath = r"C:\Temp\scriptTesting\domain_test.mxd"
def test_mxdobj_properties():
    mxdobj = mxd.MxdObj(mxdpath)
    assert mxdobj.path == mxdpath
    assert mxdobj.layer_names_array == [u'test_fv']
    assert isinstance(mxdobj.layer_obj_array, list)

