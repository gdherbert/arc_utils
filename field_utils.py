__AUTHOR__ = 'Grant Herbert'
"""utilities for working with fields"""

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


def gdb_report_fcs(gdb):
    """output a report of all fields in all featureclasses from a geodatabase
    to the geodtaabse directory or user folder
    FeatureDataset, FeatureClass, FieldName, FieldAlias, BaseName, DefaultValue,
    FieldType,Required,Editable,isNullable, FieldLength, FieldPrecision,
    FieldScale, FieldDomain"""
    startTime = datetime.datetime.today()
    startDateString = startTime.strftime('%Y%m%d')
    try:
        default_env = arcpy.env.workspace
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        if desc.Path:
            reportDir = desc.Path
        else:
            reportDir = os.environ['USERPROFILE']
            if os.path.exists(reportDir + "\\Documents"):
                reportDir = reportDir + "\\Documents"
        logFileName = "_GDBFCReport " + startDateString + ".csv"
        logFilePath = os.path.join(reportDir, logFileName)
        print "Report file: {0}".format(logFilePath)
        #list all datasets
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        #write out gdb info, fields etc
        with open(logFilePath, "w") as logFile:
            logFile.write("Geodatabase: {0}\n".format(gdb))
            logFile.write("Dataset,FeatureClass,FieldName,FieldAlias,BaseName,",
                            "DefaultValue,FieldType,Required,Editable,isNullable,",
                            "FieldLength,FieldPrecision,FieldScale,FieldDomain\n")
            for ds in datasets:
                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                    print "Processing Dataset: {0} \ FeatureClass: {1}".format(ds, fc)
                    try:
                        fields = arcpy.ListFields(fc)
                        for field in fields:
                            logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},",
                                "{9},{10},{11},{12},{13}\n".format(ds, fc,
                                 field.name, field.aliasName, field.baseName,
                                 field.defaultValue, field.type, field.required,
                                 field.editable, field.isNullable, field.length,
                                 field.precision, field.scale, field.domain))
                    except:
                        print arcpy.GetMessages()
                        continue

    except:
        print arcpy.GetMessages()
    finally:
        arcpy.env.workspace = default_env
        print "Completed"


def gdb_export_domains(gdb):
    """output all the domains in a geodatabase
    to dbf files to the geodatabase directory or user folder"""
    try:
        default_env = arcpy.env.workspace
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        domains = desc.domains
        if desc.Path:
            reportDir = desc.Path
        else:
            reportDir = os.environ['USERPROFILE']
            if os.path.exists(reportDir + "\\Documents"):
                reportDir = reportDir + "\\Documents"
        for domain in domains:
            #export the domains to tables in the gdb
            print 'Exporting {0} domain to dbf in {1}'.format(domain, reportDir)
            table = os.path.join(gdb, arcpy.ValidateTableName(domain, gdb))
            try:
                arcpy.DomainToTable_management(gdb, domain, table,
                'field','description', '#')
                #export the table to dbf
                arcpy.TableToDBASE_conversion(Input_Table=table, Output_Folder=reportDir)
                #clean up the table
                arcpy.Delete_management(table)
            except:
                print arcpy.GetMessages()
                continue
    except:
        print arcpy.GetMessages()
    finally:
        arcpy.env.workspace = default_env
        print "Completed"