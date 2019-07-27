from arc_utils import table
import collections
import os

def test_tableobj_properties(testdata2):
    # test table object properties
    testdata = testdata2
    print(testdata.gdb)
    print(testdata.fc1)
    tbl = table.TableObj(testdata.fc1)
    assert tbl.name == 'test_fc'
    assert tbl.path == testdata.fc1
    assert tbl.type == u'Point'
    assert tbl.fields == [u'OBJECTID', u'Shape', u'ftext', u'fint']
    assert tbl.fields2 == [u'ftext', u'fint']
    assert tbl.field_dict['Shape']['type'] == u'Geometry'
    assert tbl.field_dict['ftext']['aliasName']== u'ftext'
    assert tbl.field_dict['OBJECTID']['required']== True
    assert tbl.field_dict['fint']['type']== u'SmallInteger'


def test_tableobj_methods(testdata2):
    # test table object methods
    testdata = testdata2
    tbl = table.TableObj(testdata.fc1)
    ftext_set = tbl.get_field_value_set('ftext')

    assert isinstance(ftext_set, set)
    assert sorted(ftext_set) == [u'NULL', 'val02', 'val1', 'val2']
    assert tbl.get_max_field_value('ftext') == 'val2'
    assert tbl.get_max_field_value('ftext', True) == 'val02'
    assert tbl.get_max_field_value_length('ftext') == 4
    assert tbl.get_field_value_set('fint') == set([4, 5, 7, 10, u'NULL'])
    assert tbl.get_max_field_value('fint') == 10
    assert tbl.get_max_field_value_length('fint') == 2
    multi_field = tbl.get_multiple_field_value_set(['ftext', 'fint'])
    assert isinstance(multi_field, set)
    assert sorted(multi_field) == [u'NULL:5', u'val1:0', u'val1:10', u'val1:4', u'val1:5', u'val2:5', u'val2:7']
    assert tbl.fields == [u'OBJECTID', u'Shape', u'ftext', u'fint']
    assert tbl.fields2 == [u'ftext', u'fint']
    result = tbl.compare_field_values_to_domain('ftext', testdata.gdb, "ftext_coded")
    assert result.match == ['val2', 'val1']
    assert result.unmatched == ['NULL']
    result = tbl.compare_field_values_to_domain('fint', testdata.gdb, "fint_range")
    result.match.sort()
    assert result.match == [4, 5, 7, 10]
    assert result.unmatched == [u'NULL']


def test_table_fc_methods(testdata):
    # test non-object table methods
    #table.compare_schema(testdata.fc, testdata.fc2)
    pass
