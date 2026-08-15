from arc_utils import gdb
from arc_utils import table
import pathlib


class PathWrapper(object):
    def __init__(self, path):
        self.path = path

def test_gdb_properties(testdatabase):
    gdbpath = testdatabase.gdb
    gdbobj = gdb.GDBObj(gdbpath)
    assert gdbobj.path == gdbpath
    assert isinstance(gdbobj.feature_class_names, list)
    assert isinstance(gdbobj.table_names, list)
    assert isinstance(gdbobj.domain_names, list)

def test_gdb_content(testdatabase):
    gdbpath = testdatabase.gdb
    gdbobj = gdb.GDBObj(gdbpath)
    assert sorted(gdbobj.get_feature_class_names()) == ['test_fc1', 'test_fc2']
    assert sorted(gdbobj.get_all_domain_names()) == ['fint_range', 'ftext_coded']


def test_gdb_returns_featureclass_tableobjs(testdatabase):
    gdbobj = gdb.GDBObj(testdatabase.gdb)

    featureclass_objs = gdbobj.get_feature_class_objs()

    assert all(isinstance(featureclass, table.TableObj) for featureclass in featureclass_objs)
    assert sorted(featureclass.name for featureclass in featureclass_objs) == ['test_fc1', 'test_fc2']


def test_gdb_returns_table_tableobjs(testdatabase):
    gdbobj = gdb.GDBObj(testdatabase.gdb)

    table_objs = gdbobj.get_table_objs()

    assert all(isinstance(table_obj, table.TableObj) for table_obj in table_objs)
    assert [table_obj.name for table_obj in table_objs] == ['test_table']


def test_gdb_accepts_pathlike_and_wrapper_inputs(testdatabase):
    gdbobj_pathlike = gdb.GDBObj(pathlib.Path(testdatabase.gdb))
    gdbobj_wrapper = gdb.GDBObj(PathWrapper(testdatabase.gdb))
    assert sorted(gdbobj_pathlike.get_feature_class_names()) == ['test_fc1', 'test_fc2']
    assert sorted(gdbobj_wrapper.get_all_domain_names()) == ['fint_range', 'ftext_coded']
