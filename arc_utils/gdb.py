# -*- coding: utf-8 -*-
"""utilities for working with geodatabases and reporting on geodatabase contents
"""
from __future__ import print_function, unicode_literals, absolute_import
import os
import arcpy
from .output import get_valid_output_path
from .output import output_msg

class GDBObj(object):
    """ provide properties for working with a GDB
    Usage: gdb = arc_utils.gdb.GDBObj(path)
    :param
        path: a string representing a GDB connection/path
    """
    def __init__(self, gdb_path):
        """ sets up reference to table
        adds properties and methods
        """
        self.path = gdb_path
        self.describe_obj = self._describe_object()
        self.feature_classes = self.get_feature_class_names()
        self.tables = self.get_table_names()
        self.domain_names = self.get_all_domain_names()

    def _describe_object(self):
        """ returns describe object"""
        return arcpy.Describe(self.path)
        
    def get_feature_class_names(self):
        """ get a list of all the featureclass names"""
        fc_list = []
        temp_ws = arcpy.env.workspace
        arcpy.env.workspace = self.path
        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []
        for dataset in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=dataset):
                fc_list.append(fc)
        arcpy.env.workspace = temp_ws
        return fc_list
        
    def get_table_names(self):
        """ get a list of all the table names"""
        tbl_list = []
        temp_ws = arcpy.env.workspace
        arcpy.env.workspace = self.path
        tbls = arcpy.ListTables()
        for tbl in tbls:
            tbl_list.append(tbl)
        arcpy.env.workspace = temp_ws
        return tbl_list

    def get_all_domain_names(self):
        domain_names = []
        domains = arcpy.da.ListDomains(self.path)
        for domain in domains:
            domain_names.append(domain.name)
        return domain_names


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
    default_env = arcpy.env.workspace
    try:
        desc = arcpy.Describe(geodatabase)
        arcpy.env.workspace = geodatabase
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


def export_all_domains(geodatabase, workspace=None):
    """Output all the domains in a geodatabase
    to tables in a workspace.

    :param geodatabase {String}:
        Path or reference to input geodatabase.
    
    :param workspace {String}: Optional
        Path to output folder or geodatabase. Defaults to input geodatabase.
    """
    try:
        if not workspace:
            workspace = geodatabase
        domains = arcpy.da.ListDomains(geodatabase)
        for domain in domains:
            dname = arcpy.ValidateTableName(domain.name + '_domain', workspace)
            output = os.path.join(workspace, dname)
            if workspace != geodatabase:
                output += '.txt'
            output_msg('Exporting {0} domain to {1}'.format(domain.name, dname))
            arcpy.DomainToTable_management(geodatabase, domain.name, output, "codedValues", 'description')

    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        output_msg("Completed")


def import_tables_as_domains(tables, geodatabase):
    """import tables as domains into geodatabase. Expects fields 'codedValues' and 'description'
    
    :param tables {string}
        path or array of paths of input tables containing domain data
    
    :param geodatabase
        Path or reference to geodatabase."""
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