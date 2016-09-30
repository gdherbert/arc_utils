"""utilities for working with geodatabases"""
__AUTHOR__ = 'Grant Herbert'

import arcpy
import os
from arcutils.outpututils import output_msg
from arcutils.outpututils import get_valid_output_path


def report_all_fields(geodatabase):
    """Create a cvs report of all fields in all featureclasses/tables from a geodatabase
    to the geodatabase directory or user folder.

    geodatabase {String}:
        Path or reference to a geodatabase.
    """
    import datetime

    gdb = geodatabase
    start_time = datetime.datetime.today()
    start_date_string = start_time.strftime('%Y%m%d')
    default_env = arcpy.env.workspace

    try:
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        gdb_name = desc.name.split(".")[0]

        report_dir = get_valid_output_path(desc.Path)

        log_file_name = "{}_GDBFCReport_{}.csv".format(gdb_name, start_date_string)
        log_file_path = os.path.join(report_dir, log_file_name)
        output_msg("Report file: {0}".format(log_file_path))
        # list all datasets
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        # write out gdb info, fields etc
        with open(log_file_path, "w") as logFile:
            logFile.write("Geodatabase: {0}\n".format(gdb))
            logFile.write(
                "Dataset,FeatureClass,FieldName,FieldAlias,BaseName,DefaultValue,FieldType,Required,Editable,isNullable,FieldLength,FieldPrecision,FieldScale,FieldDomain\n")
            for tbl in arcpy.ListTables():
                output_msg("Processing Table: {0}".format(tbl))
                try:
                    fields = arcpy.ListFields(tbl)
                    for field in fields:
                        logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format("", tbl,
                                                                                                             field.name,
                                                                                                             field.aliasName,
                                                                                                             field.baseName,
                                                                                                             field.defaultValue,
                                                                                                             field.type,
                                                                                                             field.required,
                                                                                                             field.editable,
                                                                                                             field.isNullable,
                                                                                                             field.length,
                                                                                                             field.precision,
                                                                                                             field.scale,
                                                                                                             field.domain))
                    # fields listed, add a blank line
                    logFile.write("\n")

                except Exception as e:
                    output_msg(str(e.args[0]))
                    output_msg(arcpy.GetMessages())
                    continue

            for dataset in datasets:
                for fc in arcpy.ListFeatureClasses(feature_dataset=dataset):
                    output_msg("Processing Dataset: {0} \ FeatureClass: {1}".format(dataset, fc))
                    try:
                        fields = arcpy.ListFields(fc)
                        for field in fields:
                            logFile.write(
                                "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format(dataset, fc,
                                                                                                       field.name,
                                                                                                       field.aliasName,
                                                                                                       field.baseName,
                                                                                                       field.defaultValue,
                                                                                                       field.type,
                                                                                                       field.required,
                                                                                                       field.editable,
                                                                                                       field.isNullable,
                                                                                                       field.length,
                                                                                                       field.precision,
                                                                                                       field.scale,
                                                                                                       field.domain))
                        # fields listed, add a blank line
                        logFile.write("\n")

                    except Exception as e:
                        output_msg(str(e.args[0]))
                        output_msg(arcpy.GetMessages())
                        continue

    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        arcpy.env.workspace = default_env
        output_msg("Completed")


def export_all_domains(geodatabase):
    """Output all the domains in a geodatabase
    to dbf files in the geodatabase directory or user folder.

    geodatabase {String}:
        Path or reference to a geodatabase.
    """
    gdb = geodatabase
    default_env = arcpy.env.workspace
    try:
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        domains = desc.domains

        report_dir = get_valid_output_path(desc.Path)

        for domain in domains:
            # export the domains to tables in the gdb
            table = os.path.join(gdb, arcpy.ValidateTableName(domain, gdb))
            try:
                arcpy.DomainToTable_management(gdb, domain, table,
                                               'field', 'description', '#')
                # export the table to dbf
                output_msg('Exporting {0} domain to dbf in {1}'.format(domain, report_dir))
                arcpy.TableToDBASE_conversion(Input_Table=table, Output_Folder=report_dir)
                # clean up the table
                arcpy.Delete_management(table)
            except Exception as e:
                output_msg(arcpy.GetMessages())
                continue
    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        arcpy.env.workspace = default_env
        output_msg("Completed")
