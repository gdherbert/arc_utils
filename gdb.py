# -*- coding: utf-8 -*-
"""utilities for working with geodatabases and reporting on geodatabase contents
"""
from __future__ import print_function, unicode_literals, absolute_import
import arcpy
import os
from arcutils.output import output_msg
from arcutils.output import get_valid_output_path

#TODO split into 3 - get all FC, create formatted string output, write to file. use io
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

def extract_domains(gdb, workspace):
    """extract all domains to table"""
    domains = arcpy.da.ListDomains(gdb)
    for domain in domains:
        dname = arcpy.ValidateTableName(domain.name, workspace)
        dname = workspace + "\\" + dname
        arcpy.DomainToTable_management(gdb, domain.name, dname, "codedValues", 'descrip')

def export_all_domains(geodatabase, workspace=None):
    """Output all the domains in a geodatabase
    to tables in a workspace.
    :param geodatabase {String}:
        Path or reference to a geodatabase.
    :param output_folder {String}
        optional path to output folder. If not supplied defaults to gdb
    """
    try:
        if not workspace:
            workspace = geodatabase
        domains = arcpy.da.ListDomains(geodatabase)
        for domain in domains:
            dname = arcpy.ValidateTableName(domain.name + '_domain', workspace)
            output = os.path.join(workspace, dname)
            output_msg('Exporting {0} domain to {1}'.format(domain.name, dname))
            arcpy.DomainToTable_management(geodatabase, domain.name, output, "codedValues", 'description')

    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        output_msg("Completed")


def import_tables_as_domains(tables, geodatabase):
    """import tables as domains into geodatabase
    :param tables {string}
        path or array of paths
    :param geodatabase
        Path or reference to a geodatabase."""
    try:
        for table in tables:
            desc = arcpy.Describe(table)
            dname = desc.name.replace("_domain", "")
            arcpy.TableToDomain_management(table, "codedValues", "description", geodatabase, dname)
    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        output_msg("Completed")