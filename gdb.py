from __future__ import print_function, unicode_literals, absolute_import
"""utilities for working with geodatabases and reporting on geodatabase contents
"""

import arcpy
import os
from arcutils.output import output_msg
from arcutils.output import get_valid_output_path

def report_all_fc_as_text(geodatabase, output_file=None, sep='\t'):
    """Create a text report of all fields in all featureclasses/tables from a geodatabase
    to specified output file.
    :param geodatabase {String}
        Path or reference to a geodatabase.
    :param output_file {String}
        Path or reference to a text file. If not supplied defaults to gdb directory.
    :param sep {String}
        seperator value (eg ',' or r'\t'
    """
    gdb = geodatabase
    default_env = arcpy.env.workspace
    try:
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        if not output_file:
            path = get_valid_output_path(desc.Path)
            output_file = os.path.join(path, desc.name.split(".")[0] + ".txt")

        output_msg("Writing to: {0}".format(output_file))
        # list all datasets
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        # write out gdb info, fields etc
        with open(output_file, "w") as logFile:
            header = ["FCDataset","Feature"]
            atts = ['name', 'baseName', 'aliasName', 'type', 'length', 'precision', 'scale',
                    'domain', 'defaultValue', 'editable', 'isNullable', 'required']
            header.extend(atts)
            header_output = sep.join(["{}".format(i) for i in header])
            logFile.write(header_output + "\n")
            for tbl in arcpy.ListTables():
                output_msg("Processing Table: {0}".format(tbl))
                try:
                    fields = arcpy.ListFields(tbl)
                    str_output = ""
                    line_start = "{0}{1}{2}{1}".format("", sep, tbl)
                    for field in fields:
                        str_output += line_start + sep.join(["{}".format(getattr(field, i)) for i in atts])
                        str_output += "\n"
                    logFile.write(str_output)

                except Exception as e:
                    output_msg(str(e.args[0]))
                    output_msg(arcpy.GetMessages())
                    continue

            for dataset in datasets:
                for fc in arcpy.ListFeatureClasses(feature_dataset=dataset):
                    output_msg("Processing Dataset: {0} \ FeatureClass: {1}".format(dataset, fc))
                    try:
                        fields = arcpy.ListFields(fc)
                        str_output = ""
                        line_start = "{0}{1}{2}{1}".format(dataset, sep, fc)
                        for field in fields:
                            str_output += line_start + sep.join(["{}".format(getattr(field, i)) for i in atts])
                            str_output += "\n"
                        logFile.write(str_output)

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


def export_all_domains_as_dbf(geodatabase, output_folder=None):
    """Output all the domains in a geodatabase
    to dbf files in the geodatabase directory or user folder.
    :param geodatabase {String}:
        Path or reference to a geodatabase.
    :param output_folder {String}
        optional path to output folder. If not supplied defaults to gdb folder
    """
    gdb = geodatabase
    default_env = arcpy.env.workspace
    try:
        desc = arcpy.Describe(gdb)
        arcpy.env.workspace = gdb
        domains = desc.domains
        if not output_folder:
            output_folder = get_valid_output_path(desc.Path)

        for domain in domains:
            # export the domains to tables in the gdb
            table = os.path.join(gdb, arcpy.ValidateTableName(domain, gdb))
            try:
                arcpy.DomainToTable_management(gdb, domain, table,
                                               'field', 'description', '#')
                # export the table to dbf
                output_msg('Exporting {0} domain to dbf in {1}'.format(domain, output_folder))
                arcpy.TableToDBASE_conversion(Input_Table=table, Output_Folder=output_folder)
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
