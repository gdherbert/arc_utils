from arc_utils import gdb
import pathlib


class PathWrapper(object):
    def __init__(self, path):
        self.path = path

def test_gdb_properties(testdatabase):
    gdbpath = testdatabase.gdb
    gdbobj = gdb.GDBObj(gdbpath)
    assert gdbobj.path == gdbpath
    assert isinstance(gdbobj.feature_classes, list)
    assert isinstance(gdbobj.domain_names, list)

def test_gdb_content(testdatabase):
    gdbpath = testdatabase.gdb
    gdbobj = gdb.GDBObj(gdbpath)
    assert sorted(gdbobj.get_feature_class_names()) == ['test_fc1', 'test_fc2']
    assert sorted(gdbobj.get_all_domain_names()) == ['fint_range', 'ftext_coded']


def test_gdb_accepts_pathlike_and_wrapper_inputs(testdatabase):
    gdbobj_pathlike = gdb.GDBObj(pathlib.Path(testdatabase.gdb))
    gdbobj_wrapper = gdb.GDBObj(PathWrapper(testdatabase.gdb))
    assert sorted(gdbobj_pathlike.get_feature_class_names()) == ['test_fc1', 'test_fc2']
    assert sorted(gdbobj_wrapper.get_all_domain_names()) == ['fint_range', 'ftext_coded']
