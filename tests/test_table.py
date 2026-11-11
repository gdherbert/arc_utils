from arc_utils import table
import collections
import os
import pathlib
import pytest


class PathWrapper(object):
    def __init__(self, path):
        self.path = path

def test_tableobj_properties(testdatabase):
    # test table object properties
    testdata = testdatabase
    tbl = table.TableObj(testdata.fc1)
    assert tbl.name == 'test_fc1'
    assert tbl.path == testdata.fc1
    assert tbl.type == u'Point'
    assert tbl.fields == [u'OBJECTID', u'Shape', u'ftext', u'fint']
    assert tbl.fields2 == [u'ftext', u'fint']
    assert tbl.field_dict['Shape']['type'] == u'Geometry'
    assert tbl.field_dict['ftext']['aliasName']== u'ftext'
    assert tbl.field_dict['OBJECTID']['required']== True
    assert tbl.field_dict['fint']['type']== u'SmallInteger'


def test_tableobj_single_text_field_methods(testdatabase):
    # test table object methods
    tbl = table.TableObj(testdatabase.fc1)
    ftext_set = tbl.get_field_value_set('ftext')
    assert isinstance(ftext_set, set)
    assert sorted(ftext_set) == [u'NULL', 'val02', 'val1', 'val2']
    assert tbl.get_max_field_value('ftext') == 'val2'
    assert tbl.get_max_field_value('ftext', lengthcomp=True) == 'val02'
    assert tbl.get_max_field_value_length('ftext') == 5


def test_tableobj_single_integer_field_methods(testdatabase):
    # test table object methods
    tbl = table.TableObj(testdatabase.fc1)
    fint_set = tbl.get_field_value_set('fint')
    assert isinstance(fint_set, set)
    assert tbl.get_field_value_set('fint') == set([4, 5, 7, 10, u'NULL'])
    assert tbl.get_max_field_value('fint') == 10
    assert tbl.get_max_field_value_length('fint') == 2


def test_tableobj_multi_field_methods(testdatabase):
    # test table object methods
    tbl = table.TableObj(testdatabase.fc1)
    multi_field = tbl.get_multiple_field_value_set(['ftext', 'fint'])
    assert isinstance(multi_field, set)
    assert sorted(multi_field) == [u'<Null>:5', u'val02:7', u'val1:10', u'val1:4', u'val1:<Null>', u'val2:5', u'val2:7']
   
    

def test_tableobj_compare_methods(testdatabase):
    # test table object compare methods
    tbl = table.TableObj(testdatabase.fc1)
    result = tbl.compare_field_values_to_domain('fint', testdatabase.gdb, "fint_range")
    result.match.sort()
    assert result.match == [4, 5, 7, 10]
    assert result.unmatched == []

    result = tbl.compare_field_values_to_domain('ftext', testdatabase.gdb, "ftext_coded")
    result.match.sort()
    result.unmatched.sort()
    assert result.match == ['val1', 'val2']
    assert result.unmatched == ['NULL', 'val02']


def test_table_fc_methods(testdatabase):
    # test non-object table methods
    result = table.compare_schema(testdatabase.fc1, testdatabase.fc2)
    expected_result = ["OBJECTID field same in both","Shape field same in both","fint field same in both","ftext field same in both"]
    assert result == expected_result


def test_table_fc_methods_with_pathlike_and_wrapper_inputs(testdatabase):
    result = table.compare_schema(pathlib.Path(testdatabase.fc1), table.TableObj(PathWrapper(testdatabase.fc2)))
    expected_result = ["OBJECTID field same in both","Shape field same in both","fint field same in both","ftext field same in both"]
    assert result == expected_result


def test_tableobj_invalid_path_raises_valueerror():
    with pytest.raises(ValueError, match="invalid path"):
        table.TableObj("invalidpath")


def test_get_field_value_set_reraises_cursor_errors(monkeypatch, testdatabase):
    tbl = table.TableObj(testdatabase.fc1)
    error = RuntimeError("cursor failed")
    monkeypatch.setattr(table.arcpy.da, "SearchCursor", lambda *args, **kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(RuntimeError) as raised:
        tbl.get_field_value_set("ftext")

    assert raised.value is error


def test_find_duplicate_field_values_reraises_cursor_errors(monkeypatch, testdatabase):
    tbl = table.TableObj(testdatabase.fc1)
    error = RuntimeError("cursor failed")
    monkeypatch.setattr(table.arcpy.da, "SearchCursor", lambda *args, **kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(RuntimeError) as raised:
        tbl.find_duplicate_field_values("ftext")

    assert raised.value is error


def test_export_schema_to_csv_reraises_file_errors(monkeypatch, testdatabase):
    tbl = table.TableObj(testdatabase.fc1)
    error = OSError("file write failed")
    monkeypatch.setattr(table, "get_valid_output_path", lambda path: str(testdatabase.gdb))
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(OSError) as raised:
        tbl.export_schema_to_csv(testdatabase.gdb)

    assert raised.value is error


def test_export_fields_to_worksheet(testdatabase):
    from openpyxl import Workbook
    tbl = table.TableObj(testdatabase.fc1)
    wb = Workbook()
    ws = wb.active
    tbl.export_fields_to_worksheet(ws)

    # header row
    assert ws["A1"].value == "Field"
    assert ws["B1"].value == "Values"

    # should include ftext and fint field rows
    row_values = [ws.cell(row=r, column=1).value for r in range(2, 5)]
    assert "ftext" in row_values
    assert "fint" in row_values


def test_export_fields_to_worksheet_ignore_fields_options(testdatabase):
    from openpyxl import Workbook

    tbl = table.TableObj(testdatabase.fc1)
    tbl.ignore_fields = ["ftext"]

    default_ws = Workbook().active
    tbl.export_fields_to_worksheet(default_ws)
    assert default_ws["A2"].value == "fint"
    assert default_ws["A3"].value is None

    provided_ws = Workbook().active
    tbl.export_fields_to_worksheet(provided_ws, ignore_fields=["fint"])
    assert provided_ws["A2"].value == "ftext"
    assert provided_ws["A3"].value is None

    empty_ws = Workbook().active
    tbl.export_fields_to_worksheet(empty_ws, ignore_fields=[])
    assert {empty_ws["A2"].value, empty_ws["A3"].value} == {"ftext", "fint"}


def test_pretty_print_fields(testdatabase, capsys):
    tbl = table.TableObj(testdatabase.fc1)
    tbl.pretty_print_fields()
    output = capsys.readouterr().out
    lines = output.splitlines()

    assert "name" in lines[0]
    assert "aliasName" in lines[0]
    assert "type" in lines[0]

    assert any("OBJECTID" in line for line in lines)
    assert any("ftext" in line for line in lines)
    assert any("fint" in line for line in lines)

def test_export_field_sets_accepts_pathlike_and_wrapper_inputs(testdatabase, tmp_path):
    out_xlsx = tmp_path / "field_sets.xlsx"
    inputs = [
        pathlib.Path(testdatabase.fc1),
        table.TableObj(testdatabase.fc2),
        PathWrapper(testdatabase.fc1),
    ]
    table.export_field_sets(inputs, str(out_xlsx))
    assert out_xlsx.exists()


def test_export_field_sets_ignore_fields_options(testdatabase, tmp_path):
    from openpyxl import load_workbook

    def exported_fields(ignore_fields, filename):
        output_path = tmp_path / filename
        table.export_field_sets(testdatabase.fc1, str(output_path), ignore_fields=ignore_fields)
        workbook = load_workbook(output_path, read_only=True)
        try:
            worksheet = workbook.active
            return [worksheet.cell(row=row, column=1).value for row in range(2, worksheet.max_row + 1)]
        finally:
            workbook.close()

    assert set(exported_fields(None, "default.xlsx")) == {"ftext", "fint"}
    assert exported_fields(["ftext"], "provided.xlsx") == ["fint"]
    assert set(exported_fields([], "empty.xlsx")) == {"ftext", "fint"}


def test_find_duplicate_field_values_set_output(testdatabase):
    tbl = table.TableObj(testdatabase.fc1)
    dups = tbl.find_duplicate_field_values("ftext", output="set")
    assert isinstance(dups, set)
    assert dups == set(["val1", "val2"])

def test_find_duplicate_field_values_set_output_null_handling(testdatabase):
    tbl = table.TableObj(testdatabase.fc1)
    dups = tbl.find_duplicate_field_values("ftext", output="set")
    assert isinstance(dups, set)
    assert None not in dups
    assert dups == set(["val1", "val2"])

def test_find_duplicate_field_values_set_output_with_threshold(testdatabase):
    tbl = table.TableObj(testdatabase.fc1)
    dups = tbl.find_duplicate_field_values("ftext", output="set", threshold=4)
    assert isinstance(dups, set)
    assert dups == set(["val1"])

def test_find_duplicate_field_values_dataframe_output(testdatabase):
    pandas = pytest.importorskip("pandas")
    tbl = table.TableObj(testdatabase.fc1)
    dups = tbl.find_duplicate_field_values(["ftext", "fint"], output="df")
    assert isinstance(dups, pandas.DataFrame)
    assert "count" in dups.columns
    assert dups["count"].min() > 1

    dups_alias = tbl.find_duplicate_field_values_as_df(["ftext", "fint"])
    assert isinstance(dups_alias, pandas.DataFrame)
    assert "count" in dups_alias.columns
    assert dups_alias["count"].min() > 1


def test_find_duplicate_field_values_dataframe_null_handling(testdatabase, monkeypatch):
    pandas = pytest.importorskip("pandas")
    tbl = table.TableObj(testdatabase.fc1)

    class SearchCursor(object):
        all_rows = [
            ("val1", None),
            ("val1", None),
            ("val2", 1),
            ("val2", 1),
            (None, None),
            (None, None),
        ]

        def __init__(self, fields):
            self.rows = self.all_rows if len(fields) > 1 else [(row[0],) for row in self.all_rows]

        def __iter__(self):
            return iter(self.rows)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr(
        table.arcpy.da,
        "SearchCursor",
        lambda table_path, fields, **kwargs: SearchCursor(fields),
    )

    single_field_dups = tbl.find_duplicate_field_values(["ftext"], output="df")
    assert not single_field_dups["ftext"].isna().any()

    multi_field_dups = tbl.find_duplicate_field_values(["ftext", "fint"], output="df")
    partial_null_dups = multi_field_dups[
        (multi_field_dups["ftext"] == "val1") & multi_field_dups["fint"].isna()
    ]
    assert partial_null_dups.iloc[0]["count"] == 2
    assert not multi_field_dups[["ftext", "fint"]].isna().all(axis=1).any()


def test_find_duplicate_field_values_dataframe_output_with_threshold(testdatabase):
    threshold = 3
    pandas = pytest.importorskip("pandas")
    tbl = table.TableObj(testdatabase.fc1)
    dups = tbl.find_duplicate_field_values(["ftext"], threshold=threshold, output="df")
    assert isinstance(dups, pandas.DataFrame)
    assert "count" in dups.columns
    assert dups["count"].min() >= 3

    dups_alias = tbl.find_duplicate_field_values_as_df(["ftext"], threshold=threshold)
    assert isinstance(dups_alias, pandas.DataFrame)
    assert "count" in dups_alias.columns
    assert dups_alias["count"].min() >= 3


def test_find_duplicate_field_values_dataframe_output_with_threshold_returns_empty(testdatabase):
    threshold = 100
    pandas = pytest.importorskip("pandas")
    tbl = table.TableObj(testdatabase.fc1)
    dups = tbl.find_duplicate_field_values(["ftext"], threshold=threshold, output="df")
    assert isinstance(dups, pandas.DataFrame)
    assert "count" in dups.columns
    assert dups.empty

    dups_alias = tbl.find_duplicate_field_values_as_df(["ftext"], threshold=threshold)
    assert isinstance(dups_alias, pandas.DataFrame)
    assert "count" in dups_alias.columns
    assert dups_alias.empty
