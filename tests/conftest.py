"""module wide test fixtures"""
import pytest
import arcpy
import os
import random
import collections

testfolder = 'tests'

#@pytest.fixture(scope='module')
#def testdata(pytestconfig):
#    gdb = "arc_utils_test.gdb"
#    fc_names = ['test_fc', 'test_fc2']
#    print('folder {}, gdb {}, fc {}'.format(testfolder, gdb, fc_names))
#    result = collections.namedtuple('testdata', 'gdb, test_fc, test_fc2')
#    result.gdb = str(pytestconfig.rootdir.join(testfolder).join(gdb))
#    result.fc1 = str(pytestconfig.rootdir.join(testfolder).join(gdb).join(fc_names[0]))
#    result.fc2 = str(pytestconfig.rootdir.join(testfolder).join(gdb).join(fc_names[1]))
#    print(result)
#    return result

@pytest.fixture(scope='module')
def testgdb(pytestconfig):
    gdb_name = "arc_utils_test_tmp.gdb"
    return str(pytestconfig.rootdir.join(testfolder).join(gdb_name))

@pytest.fixture(scope='module')
def testmxd(pytestconfig):
    mxd_name = "arc_utils_test.mxd"
    return str(pytestconfig.rootdir.join(testfolder).join(mxd_name))

@pytest.fixture(scope='module')
def testaprx(pytestconfig):
    aprx_name = "arc_utils_test_pro.aprx"
    return str(pytestconfig.rootdir.join(testfolder).join(aprx_name))

@pytest.fixture(scope='module')
def testdatabase(request, testgdb):
    # create a testing gdb
    print("Creating test geodatabase")
    testgdbpath = testgdb # os.path.join(arcpy.env.scratchFolder, "arc_utils_test.gdb")
    if arcpy.Exists(testgdbpath):
        print("Deleting " + testgdbpath)
        arcpy.Delete_management(testgdbpath)
    arcpy.CreateFileGDB_management(os.path.dirname(testgdbpath), os.path.basename(testgdbpath))
    # add a domain for each field in testfc
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
    print("Creating test featureclasses")
    sr = arcpy.SpatialReference(4326)
    fc_names = ['test_fc', 'test_fc2']
    fc_paths = []
    fc_fields = (('ftext', 'TEXT', None, None, 20, '', 'NULLABLE', 'NON_REQUIRED', ftext_dom_name),
                 ('fint', 'SHORT', 0, 0, 0, '', 'NULLABLE', 'NON_REQUIRED', fint_dom_name))

    for name in fc_names:
        arcpy.CreateFeatureclass_management(testgdbpath, name, "POINT", spatial_reference=sr)
        fc = os.path.join(testgdbpath, name)
        fc_paths.append(fc)
        for fc_field in fc_fields:
            arcpy.AddField_management(fc, *fc_field)
        print("loading data")
        records = (("val1", None),("val1", 4), ("val1", 4), ("val2", 7), ("val02", 7), ("val1", 10), ("val2", 5), ("val1", 10), ("val2", 5), ("val1", None), (None, 5))
        with arcpy.da.InsertCursor(fc, ["ftext", "fint", "SHAPE@XY"]) as cursor:
            for key, val in records:
                lon = -122.3 + float(random.randint(-9, 9)) / 100
                lat = 47.6 + float(random.randint(-9, 9)) / 100
                cursor.insertRow([key, val, (lon, lat)])

    result = collections.namedtuple('testdata', 'gdb, test_fc1, test_fc2')
    result.gdb = testgdbpath
    result.fc1 = fc_paths[0]
    result.fc2 = fc_paths[1]

    def testdata_teardown():
        print('Deleting test geodatabase')
        arcpy.Delete_management(testgdbpath)

    request.addfinalizer(testdata_teardown)
    return result