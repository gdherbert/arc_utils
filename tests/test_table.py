from arc_utils import table
import pytest
import arcpy
import collections
import random
import os

@pytest.fixture(scope='module')
def testdata(request):
    # create a testing gdb
    print("Creating test geodatabase")
    testgdbpath = os.path.join(arcpy.env.scratchFolder, "arc_utils_test.gdb")
    if arcpy.Exists(testgdbpath):
        print("Deleting " + testgdbpath)
        arcpy.Delete_management(testgdbpath)
    arcpy.CreateFileGDB_management(arcpy.env.scratchFolder, "arc_utils_test.gdb")
    #add a domain for each field in testfc
    ftext_dom_name = "ftext_coded"
    fint_dom_name = "fint_range"
    arcpy.CreateDomain_management(in_workspace=testgdbpath,
                                                 domain_name=ftext_dom_name,
                                                 domain_description="text domain",
                                                 field_type="TEXT",
                                                 domain_type="CODED")
    arcpy.CreateDomain_management(in_workspace=testgdbpath,
                                                domain_name=fint_dom_name,
                                                field_type="SHORT",
                                                domain_type="RANGE")
    ftextDict = {"val1": "val1", "val2": "val2", "val3": "val3"}
    for code in ftextDict:
        arcpy.AddCodedValueToDomain_management(testgdbpath, ftext_dom_name, code, ftextDict[code])
    arcpy.SetValueForRangeDomain_management(testgdbpath, fint_dom_name, 1, 12)
    print("Creating test featureclass")
    sr = arcpy.SpatialReference(4326)
    fc_name = 'test_fc'
    fc_fields = (('ftext', 'TEXT', None, None, 20, '', 'NULLABLE', 'NON_REQUIRED', ftext_dom_name),
                 ('fint', 'SHORT', 0, 0, 0, '', 'NULLABLE', 'NON_REQUIRED', fint_dom_name))
    fc = arcpy.CreateFeatureclass_management(testgdbpath, fc_name, "POINT", spatial_reference=sr)
    for fc_field in fc_fields:
        arcpy.AddField_management(fc, *fc_field)
    print("loading data")
    records = (("val1", 4), ("val2", 7), ("val1", 10), ("val2", 4), ("val1", 7), ("val2", 9))
    with arcpy.da.InsertCursor(fc, ["ftext", "fint", "SHAPE@XY"]) as cursor:
        for key, val in records:
            lon = 122.3 + float(random.randint(-9, 9)) / 100
            lat = 47.6 + float(random.randint(-9, 9)) / 100
            cursor.insertRow([key, val, (lon, lat)])
    # insert a couple of rows with null
    with arcpy.da.InsertCursor(fc, ["ftext", "fint", "SHAPE@XY"]) as cursor:
        cursor.insertRow(["val1", None, (122.399, 47.699)])
        cursor.insertRow([None, 5, (122.399, 47.699)])

    result = collections.namedtuple('testdata', 'gdb, fc')
    result.gdb = testgdbpath
    result.fc = fc

    def testdata_teardown():
        arcpy.Delete_management(testgdbpath)

    request.addfinalizer(testdata_teardown)
    return result


def test_tableobj_properties(testdata):
    # test table object properties
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
    assert tbl.get_field_value_set('ftext') == set(['val2', 'val1', u'NULL'])
    assert tbl.get_max_field_value('ftext') == 'val2'
    assert tbl.get_max_field_value_length('ftext') == 4
    assert tbl.get_field_value_set('fint') == set([4, 5, 7, 9, 10, u'NULL'])
    assert tbl.get_max_field_value('fint') == 10
    assert tbl.get_max_field_value_length('fint') == 2


def test_table_fc_methods(testdata):
    # test non-object table methods
    assert table.get_field_value_set(testdata.fc, 'ftext') == set(['val2', 'val1', u'NULL'])
    assert table.get_max_field_value(testdata.fc, 'ftext') == 'val2'
    assert table.get_max_field_value_length(testdata.fc, 'ftext') == 4
    assert table.get_field_value_set(testdata.fc, 'fint') == set([4, 5, 7, 9, 10, u'NULL'])
    assert table.get_max_field_value(testdata.fc, 'fint') == 10
    assert table.get_max_field_value_length(testdata.fc, 'fint') == 2
    assert table.get_multiple_field_value_set(testdata.fc, ['ftext', 'fint']) == set([u'val1:10', u'NULL:5', u'val1:7', u'val1:4', u'val2:4', u'val2:7', u'val2:9', u'val1:9'])
    assert table.list_field_names(testdata.fc) == [u'OBJECTID', u'Shape', u'ftext', u'fint']
    assert table.list_field_names(testdata.fc, False) == [u'ftext', u'fint']

def test_table_fcgdb_methods(testdata):
    # test the method to compare field values to domains for coded values
    result = table.compare_field_values_to_domain(testdata.fc, 'ftext', testdata.gdb, "ftext_coded")
    assert result.match == ['val2', 'val1']
    assert result.unmatched == ['NULL']

    # test the method to compare field values to domains for a range
    result = table.compare_field_values_to_domain(testdata.fc, 'fint', testdata.gdb, "fint_range")
    assert result.match == [4, 5, 7, 9, 10]
    assert result.unmatched == [u'NULL']
