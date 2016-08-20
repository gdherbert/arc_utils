__AUTHOR__ = 'Grant Herbert'
"""utilities for working with geodatabases"""
import arcpy
import os
from arc_utils.output_msg import output_msg

def report_fields(geodatabase):
    """Create a cvs report of all fields in all featureclasses/tables from a geodatabase
    to the geodatabase directory or user folder.

    geodatabase{String}:
        Path or reference to a geodatabase.
    """
    import datetime

    gdb = geodatabase
    startTime = datetime.datetime.today()
    startDateString = startTime.strftime('%Y%m%d')

    try:
        default_env = arcpy.env.workspace
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        if os.path.isdir(desc.Path):
            reportDir = desc.Path
        else:
            reportDir = os.environ['USERPROFILE']
            if os.path.exists(reportDir + "\\Documents"):
                reportDir = reportDir + "\\Documents"
        logFileName = "_GDBFCReport " + startDateString + ".csv"
        logFilePath = os.path.join(reportDir, logFileName)
        output_msg("Report file: {0}".format(logFilePath))
        #list all datasets
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        #write out gdb info, fields etc
        with open(logFilePath, "w") as logFile:
            logFile.write("Geodatabase: {0}\n".format(gdb))
            logFile.write("Dataset,FeatureClass,FieldName,FieldAlias,BaseName,DefaultValue,FieldType,Required,Editable,isNullable,FieldLength,FieldPrecision,FieldScale,FieldDomain\n")
            for tbl in arcpy.ListTables():
                    output_msg("Processing Table: {0}".format(tbl))
                    try:
                        fields = arcpy.ListFields(tbl)
                        for field in fields:
                            logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format("",tbl,
                                 field.name, field.aliasName, field.baseName,
                                 field.defaultValue, field.type, field.required,
                                 field.editable, field.isNullable, field.length,
                                 field.precision, field.scale, field.domain))
                    except:
                        output_msg(arcpy.GetMessages())
                        continue

            for ds in datasets:
                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                    output_msg("Processing Dataset: {0} \ FeatureClass: {1}".format(ds, fc))
                    try:
                        fields = arcpy.ListFields(fc)
                        for field in fields:
                            logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format(ds, fc,
                                 field.name, field.aliasName, field.baseName,
                                 field.defaultValue, field.type, field.required,
                                 field.editable, field.isNullable, field.length,
                                 field.precision, field.scale, field.domain))
                    except:
                        output_msg(arcpy.GetMessages())
                        continue


    except Exception, e:
        output_msg(str(e))
        output_msg(arcpy.GetMessages())
    finally:
        arcpy.env.workspace = default_env
        output_msg("Completed")


def export_domains(geodatabase):
    """Output all the domains in a geodatabase
    to dbf files in the geodatabase directory or user folder.

    geodatabase{String}:
        Path or reference to a geodatabase.
    """

    gdb = geodatabase
    try:
        default_env = arcpy.env.workspace
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        domains = desc.domains
        if os.path.isdir(desc.Path):
            reportDir = desc.Path
        else:
            reportDir = os.environ['USERPROFILE']
            if os.path.exists(reportDir + "\\Documents"):
                reportDir = reportDir + "\\Documents"
        for domain in domains:
            #export the domains to tables in the gdb
            table = os.path.join(gdb, arcpy.ValidateTableName(domain, gdb))
            try:
                arcpy.DomainToTable_management(gdb, domain, table,
                'field','description', '#')
                #export the table to dbf
                output_msg('Exporting {0} domain to dbf in {1}'.format(domain, reportDir))
                arcpy.TableToDBASE_conversion(Input_Table=table, Output_Folder=reportDir)
                #clean up the table
                arcpy.Delete_management(table)
            except:
                output_msg(arcpy.GetMessages())
                continue
    except:
        output_msg(arcpy.GetMessages())
    finally:
        arcpy.env.workspace = default_env
        output_msg("Completed")

