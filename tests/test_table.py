from arc_utils import table
import collections
import os

def test_tableobj_properties(testdata):
    # test table object properties
    print(testdata.gdb)
    print(testdata.fc)
    tbl = table.TableObj(testdata.fc)

    assert tbl.path == testdata.fc
    assert tbl.type == u'Point'
    assert tbl.fields == [u'OBJECTID', u'Shape', u'ftext', u'fint']
    assert tbl.fields2 == [u'ftext', u'fint']
    assert tbl.field_dict == {u'Shape': {u'alias': u'Shape', u'length': 0, u'required': True, u'type': u'Geometry', u'name': u'Shape'},
                              u'ftext': {u'alias': u'ftext', u'length': 20, u'required': False, u'type': u'String', u'name': u'ftext'}, u'OBJECTID': {u'alias': u'OBJECTID', u'length': 4, u'required': True, u'type': u'OID', u'name': u'OBJECTID'},
                              u'fint': {u'alias': u'fint', u'length': 2, u'required': False, u'type': u'SmallInteger', u'name': u'fint'}}


def test_tableobj_methods(testdata):
    # test table object methods
    tbl = table.TableObj(testdata.fc)
    ftext_set = tbl.get_field_value_set('ftext')

    assert isinstance(ftext_set, set)
    assert sorted(ftext_set) == [u'NULL', 'val1', 'val2']
    assert tbl.get_max_field_value('ftext') == 'val2'
    assert tbl.get_max_field_value_length('ftext') == 4
    assert tbl.get_field_value_set('fint') == set([4, 5, 7, 10, u'NULL'])
    assert tbl.get_max_field_value('fint') == 10
    assert tbl.get_max_field_value_length('fint') == 2


def test_table_fc_methods(testdata):
    # test non-object table methods
    assert sorted(table.get_field_value_set(testdata.fc, 'ftext')) == [u'NULL', 'val1', 'val2']
    assert table.get_max_field_value(testdata.fc, 'ftext') == 'val2'
    assert table.get_max_field_value_length(testdata.fc, 'ftext') == 4
    assert sorted(table.get_field_value_set(testdata.fc, 'fint')) == [4, 5, 7, 10, u'NULL']
    assert table.get_max_field_value(testdata.fc, 'fint') == 10
    assert table.get_max_field_value_length(testdata.fc, 'fint') == 2
    multi_field = table.get_multiple_field_value_set(testdata.fc, ['ftext', 'fint'])
    assert isinstance(multi_field, set)
    assert sorted(multi_field) == [u'NULL:5', u'val1:0', u'val1:10', u'val1:4', u'val1:5', u'val2:5', u'val2:7']
    assert table.list_field_names(testdata.fc) == [u'OBJECTID', u'Shape', u'ftext', u'fint']
    assert table.list_field_names(testdata.fc, False) == [u'ftext', u'fint']

def test_table_fcgdb_methods(testdata):
    # test the method to compare field values to domains for coded values
    result = table.compare_field_values_to_domain(testdata.fc, 'ftext', testdata.gdb, "ftext_coded")
    assert result.match == ['val2', 'val1']
    assert result.unmatched == ['NULL']

    # test the method to compare field values to domains for a range
    result = table.compare_field_values_to_domain(testdata.fc, 'fint', testdata.gdb, "fint_range")
    result.match.sort()
    assert result.match == [4, 5, 7, 10]
    assert result.unmatched == [u'NULL']
