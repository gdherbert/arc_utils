from arc_utils import gdb

def test_gdb_properties(testdatabase):
    gdbpath = testdatabase.gdb
    gdbobj = gdb.GDBObj(gdbpath)
    assert gdbobj.path == gdbpath
    assert isinstance(gdbobj.feature_classes, list)
    assert isinstance(gdbobj.domain_names, list)

def test_gdb_content(testdatabase):
    gdbpath = testdatabase.gdb
    gdbobj = gdb.GDBObj(gdbpath)
    assert sorted(gdbobj.get_feature_class_names()) == ['test_fc', 'test_fc2']
    assert sorted(gdbobj.get_all_domain_names()) == ['fint_range', 'ftext_coded']
