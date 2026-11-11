from arc_utils import gdb
from arc_utils import table
import pathlib
import pytest


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


@pytest.mark.parametrize(
    ("method_name", "arcpy_function"),
    [
        ("get_feature_class_objs", "ListDatasets"),
        ("get_table_objs", "ListTables"),
    ],
)
def test_gdb_workspace_is_restored_when_listing_fails(monkeypatch, method_name, arcpy_function):
    monkeypatch.setattr(gdb.arcpy.env, "workspace", "original-workspace")

    def fail_listing(*args, **kwargs):
        raise RuntimeError("listing failed")

    monkeypatch.setattr(gdb.arcpy, arcpy_function, fail_listing)
    gdb_obj = object.__new__(gdb.GDBObj)
    gdb_obj.path = "target.gdb"

    with pytest.raises(RuntimeError, match="listing failed"):
        getattr(gdb_obj, method_name)()
    assert gdb.arcpy.env.workspace == "original-workspace"
    assert gdb.arcpy.env.workspace == "original-workspace"


def test_report_all_fc_as_text_restores_workspace_and_reraises(monkeypatch, tmp_path):
    monkeypatch.setattr(gdb.arcpy.env, "workspace", "original-workspace")
    monkeypatch.setattr(gdb, "_resolve_dataset_path", lambda *args, **kwargs: "target.gdb")
    monkeypatch.setattr(gdb, "_ensure_valid_path", lambda path: path)
    monkeypatch.setattr(gdb.arcpy, "Describe", lambda path: object())

    def fail_listing(*args, **kwargs):
        raise RuntimeError("listing failed")

    monkeypatch.setattr(gdb.arcpy, "ListDatasets", fail_listing)

    with pytest.raises(RuntimeError, match="listing failed"):
        gdb.report_all_fc_as_text("target.gdb", str(tmp_path / "report.txt"))

    assert gdb.arcpy.env.workspace == "original-workspace"


def test_export_all_domains_reraises_operational_errors(monkeypatch):
    error = RuntimeError("domain listing failed")
    monkeypatch.setattr(gdb, "_resolve_dataset_path", lambda *args, **kwargs: "target.gdb")
    monkeypatch.setattr(gdb, "_ensure_valid_path", lambda path: path)
    monkeypatch.setattr(gdb.arcpy.da, "ListDomains", lambda path: (_ for _ in ()).throw(error))

    with pytest.raises(RuntimeError) as raised:
        gdb.export_all_domains("target.gdb")

    assert raised.value is error


def test_import_tables_as_domains_reraises_operational_errors(monkeypatch):
    error = RuntimeError("domain import failed")
    monkeypatch.setattr(gdb, "_resolve_dataset_path", lambda *args, **kwargs: "target")
    monkeypatch.setattr(gdb, "_ensure_valid_path", lambda path: path)
    monkeypatch.setattr(gdb.arcpy, "Describe", lambda path: type("Description", (), {"name": "example_domain"})())
    monkeypatch.setattr(
        gdb.arcpy,
        "TableToDomain_management",
        lambda *args, **kwargs: (_ for _ in ()).throw(error),
    )

    with pytest.raises(RuntimeError) as raised:
        gdb.import_tables_as_domains("table", "target.gdb")

    assert raised.value is error


def test_constructors_use_consistent_invalid_path_errors(monkeypatch):
    from arc_utils import aprx

    monkeypatch.setattr(gdb, "_resolve_dataset_path", lambda *args, **kwargs: "missing")
    monkeypatch.setattr(table, "_resolve_dataset_path", lambda *args, **kwargs: "missing")
    monkeypatch.setattr(aprx, "_resolve_aprx_path", lambda *args, **kwargs: "missing")
    monkeypatch.setattr(gdb.arcpy, "Exists", lambda path: False)

    for constructor in (gdb.GDBObj, table.TableObj, aprx.AprxObj):
        with pytest.raises(ValueError, match="invalid path"):
            constructor("missing")
