__AUTHOR__ = 'Grant Herbert'
"""utilities for working with fields"""
import arcpy

def get_field_value_set(inputTable, field, charset='ascii'):
    """Get a list of unique field values given an input table,
       a field name string and an optional charset (default='ascii')
       ascii charset will force encoding with ignore option
        Returns a set"""

    try:
        valueSet = set() # set to hold unique values
        # use data access search cursor combined with, 'with'
        with arcpy.da.SearchCursor(inputTable, field) as values:
            # iterate through all values returned by Search Cursor
            for value in values:
                # Add value to set. If the value is not present,
                # it will be added. If it is present, the set will not
                # allow duplicates.
                if value[0] is None:
                    #Null value
                    valueSet.add("")
                else:
                    if charset != 'ascii':
                        valueSet.add(value[0])
                    else:
                        #if unicode strings are causing problem, try
                        valueSet.add(value[0].encode('ascii', 'ignore'))
        # return list of values
        return valueSet

    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]


def pprint_fields(table):
    """ pretty print table's fields and their properties """

    def _print(l):
        print("".join(["{:>12}".format(i) for i in l]))

    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]
    _print(atts)

    for f in arcpy.ListFields(table):
        _print(["{:>12}".format(getattr(f, i)) for i in atts])



def field_report(fc):
    """output a report of all fields in a featureclasse,
    to the geodatabase directory or user folder
    FeatureDataset, FeatureClass, FieldName, FieldAlias, BaseName, DefaultValue,
    FieldType,Required,Editable,isNullable, FieldLength, FieldPrecision,
    FieldScale, FieldDomain"""
    import datetime
    import os

    startTime = datetime.datetime.today()
    startDateString = startTime.strftime('%Y%m%d')
    default_env = arcpy.env.workspace

    try:
        print fc
        desc = arcpy.Describe(fc)
        arcpy.env.workspace = fc
        if os.path.isdir(desc.Path):
            reportDir = desc.Path
        else:
            reportDir = os.environ['USERPROFILE']
            if os.path.exists(reportDir + "\\Documents"):
                reportDir = reportDir + "\\Documents"

        logFileName = desc.baseName + "_Field_Report " + startDateString + ".csv"
        logFilePath = os.path.join(reportDir, logFileName)
        print "Report file: {0}".format(logFilePath)
        with open(logFilePath, "w") as logFile:
            logFile.write("{0}\n".format(desc.name))
            logFile.write("Dataset,FeatureClass,FieldName,FieldAlias,BaseName,")
            logFile.write("DefaultValue,FieldType,Required,Editable,isNullable,")
            logFile.write("FieldLength,FieldPrecision,FieldScale,FieldDomain\n")

            try:
                fields = arcpy.ListFields(fc)
                for field in fields:
                    logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(
                         field.name, field.aliasName, field.baseName,
                         field.defaultValue, field.type, field.required,
                         field.editable, field.isNullable, field.length,
                         field.precision, field.scale, field.domain))
            except:
                print arcpy.GetMessages()

    except:
        print arcpy.GetMessages()
    finally:
        print "Completed"
        arcpy.env.workspace = default_env