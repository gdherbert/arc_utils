# -*- coding: utf-8 -*-
"""utilities for working with tables, featureclasses and fields
"""
from __future__ import print_function, unicode_literals, absolute_import

import arcpy
from .output import get_valid_output_path
from .output import output_msg


class TableObj(object):
    """ provide properties for working with a table/featureclass
    Usage: tbl = arc_utils.table.TableObj(path)
    :param
        path: a string representing an table/featureclass
    """
    def __init__(self, table_path):
        """ sets up reference to table
        adds properties and methods
        """
        self.path = table_path
        self.type = self._get_fc_type()
        self.fields = self._list_field_names()
        self.fields2 = self._list_field_names(required=False)
        self.field_dict = self._make_field_dict()

    def _get_fc_type(self):
        d = arcpy.Describe(self.path)
        if hasattr(d, 'shapeType'):
            return d.shapeType
        elif hasattr(d, 'dataType'):
            return d.dataType
        else:
            return 'Unknown'

    def _list_field_names(self, required=True):
        """Array of field names
        """
        if required:
            f_list = [field.name for field in arcpy.ListFields(self.path)]
        else:
            f_list = [field.name for field in arcpy.ListFields(self.path) if not field.required]
        return f_list

    def _make_field_dict(self):
        """Dictionary of fields containing
        name, type, length
        """
        field_dict = dict()
        for field in arcpy.ListFields(self.path):
            field_dict[field.name] = {
                "name": field.name,
                "alias": field.aliasName,
                "type": field.type,
                "length": field.length,
                "required": field.required
            }
        return field_dict

    def get_max_field_value(self, field):
        """Largest value in the field.
        """
        result = 0
        with arcpy.da.SearchCursor(self.path, field) as values:
            for value in values:
                if value[0] is not None:
                    val = value[0]
                    if type(val) in ('str', 'unicode'):
                        if len(val) > result:
                            result = len(val)
                    else:
                        if val > result:
                            result = val
        return result

    def get_max_field_value_length(self, field):
        """Length of the maximum value in the field.
        """
        length = 0
        with arcpy.da.SearchCursor(self.path, field) as values:
            for value in values:
                if value[0] is not None:
                    val = str(value[0])
                    if len(val) > length:
                        length = len(val)
        return length

    def get_field_value_set(self, field, charset='ascii'):
        """Return set of unique field values
            :param field {String}:
                name of the field to parse
            :param: charset {String}:
                character set to use (default = 'ascii').
                Valid values are those in the Python documentation for string encode.
            :return set of unique values. Null values are represented as 'NULL'
           """
        try:
            value_set = set()  # set to hold unique values
            with arcpy.da.SearchCursor(self.path, field) as values:
                for value in values:
                    if value[0] is None:
                        value_set.add("NULL")
                    elif isinstance(value[0], (str, unicode)):
                        if charset != 'ascii':
                            value_set.add(value[0])
                        else:
                            # if unicode strings are causing problem, try
                            value_set.add(value[0].encode('ascii', 'ignore'))
                    else:
                        value_set.add(value[0])
            return value_set

        except arcpy.ExecuteError:
            output_msg(arcpy.GetMessages(2))
        except Exception as e:
            output_msg(e.args[0])

    def pretty_print(self):
        """ pretty print a table's fields and their properties
        """
        def _print(l):
            print("".join(["{:>12}".format(i) for i in l]))

        atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
                'editable', 'isNullable', 'length', 'precision',
                'required', 'scale', ]
        _print(atts)

        for f in arcpy.ListFields(self.path):
            _print(["{:>12}".format(getattr(f, i)) for i in atts])


def pprint_fields(input_fc):
    """ pretty print a table's fields and their properties
        :param input_fc {String}:
            Path or reference to feature class or table.
    """
    def _print(l):
        print("".join(["{:>12}".format(i) for i in l]))

    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]
    _print(atts)

    for f in arcpy.ListFields(input_fc):
        _print(["{:>12}".format(getattr(f, i)) for i in atts])


def get_max_field_value(input_fc, field):
    """Return either the longest string in the field,
    or the largest number.
        :param input_fc {String}:
            Path or reference to feature class or table.
        :param field {String}:
            name of the field to parse
        :return integer
    """
    result = 0
    with arcpy.da.SearchCursor(input_fc, field) as values:
            for value in values:
                if value[0] is not None:
                    val = value[0]
                    if type(val) in ('str', 'unicode'):
                        if len(val) > result:
                            result = len(val)
                    else:
                        if val > result:
                            result = val
    return result

def get_max_field_value_length(input_fc, field):
    """Length of the maximum value in the field.
    """
    length = 0
    with arcpy.da.SearchCursor(input_fc, field) as values:
        for value in values:
            if value[0] is not None:
                val = str(value[0])
                if len(val) > length:
                    length = len(val)
    return length

def get_field_value_set(inputfc, field, charset='ascii'):
    """Return set of unique field values
        :param field {String}:
            name of the field to parse
        :param: charset {String}:
            character set to use (default = 'ascii').
            Valid values are those in the Python documentation for string encode.
        :return set of unique values. Null values are represented as 'NULL'
       """
    try:
        value_set = set()  # set to hold unique values
        with arcpy.da.SearchCursor(inputfc, field) as values:
            for value in values:
                if value[0] is None:
                    value_set.add("NULL")
                elif isinstance(value[0], (str, unicode)):
                    if charset != 'ascii':
                        value_set.add(value[0])
                    else:
                        # if unicode strings are causing problem, try
                        value_set.add(value[0].encode('ascii', 'ignore'))
                else:
                    value_set.add(value[0])
        return value_set

    except arcpy.ExecuteError:
        output_msg(arcpy.GetMessages(2))
    except Exception as e:
        output_msg(e.args[0])

def get_multiple_field_value_set(input_fc, fields, sep=':'):
    """return a set of unique field values for an input table
    and any number of fields (values will be concatenated with sep)
    null values converted to 'NULL'
    :param input fc {String}
        Path or reference to feature class or table.
    :param fields {array of String values}:
        single field name or an array of field names (['Field1', 'Field2'])
    :param sep {String}:
        character to use as a separator (default = ':'
    """
    if not isinstance(fields, list):
        fieldslist = [fields]
    else:
        fieldslist = fields
    import pandas
    data = arcpy.da.TableToNumPyArray(input_fc, fieldslist, null_value='NULL')
    df = pandas.DataFrame(data)
    pandas.DataFrame.drop_duplicates(df, inplace=True)
    # concatenate values
    if len(fieldslist) > 1:
        result = df[fieldslist].apply(lambda x: sep.join(x.dropna().astype(str)), axis=1) # all types
    else:
        result = df.values.flatten()
    # return as a set
    return set(result)

#TODO - move to gdb module and import table get_field_value_set
def compare_field_values_to_domain(input_fc, fieldname, gdb, domain_name):
    """compare field values with domain values
        return a named tuple (matched = values in domain,
        unmatched = values outside of domain
        :param input_fc {string}
            Path or reference to feature class or table.
        :param fieldname {string}
            Field name
        :param gdb {string}
            Geodatabase path
        :param domain_name {string}
            Domain name in gdb
    """
    from collections import namedtuple
    nt = namedtuple('Result', 'match unmatched')
    field_values = get_field_value_set(input_fc, fieldname)
    domain_values = []
    domain_type = None
    field_in_domain = []
    field_out_domain = []
    domains = arcpy.da.ListDomains(gdb)
    for domain in domains:
        if domain.name == domain_name:
            if domain.domainType == 'CodedValue':
                domain_type = 'CodedValue'
                coded_values = domain.codedValues
                for code, descr in coded_values.items():
                    domain_values.append(code)
            elif domain.domainType == 'Range':
                domain_type = 'Range'
                domain_values.append(domain.range[0])
                domain_values.append(domain.range[1])
            break
    if domain_type == 'Range':
        #compare upper and lower bounds
        for fv in field_values:
            if fv < domain_values[0] or fv > domain_values[1]:
                field_out_domain.append(fv)
            else:
                field_in_domain.append(fv)
    else:
        for value in field_values:
            if value in domain_values:
                field_in_domain.append(value)
            else:
                field_out_domain.append(value)

    return nt(field_in_domain, field_out_domain)



def get_field_info_as_text(input_fc, sep="\t"):
    """ Create a separated output of a table's fields and their properties
        :param input_fc {String}:
            Path or reference to feature class or table.
        :param sep {String}
            Separator value to use. eg r"\t" for tab (default), "," for comma
        :return string of values with separator between
    """
    atts = ['name', 'baseName', 'aliasName', 'type', 'length', 'precision', 'scale',
            'domain', 'defaultValue', 'editable', 'isNullable', 'required']

    str_output = sep.join(["{}".format(i) for i in atts])
    str_output += "\n"
    for f in arcpy.ListFields(input_fc):
        str_output += sep.join(["{}".format(getattr(f, i)) for i in atts])
        str_output += "\n"
    return str_output


def list_field_names(input_fc, required=True):
    """Return an array of field names given an input table.
        :param input_fc {String}:
            Path or reference to feature class or table.
        :param required {Bool}
            If True, returns all fields, else only non required fields returned
        :return array of field names
    """
    f_list = []
    for f in arcpy.ListFields(input_fc):
        if required:
            f_list.append(f.name)
        else:
            if f.required:
                f_list.append(f.name)
    return f_list


def make_field_dict(input_fc, ignore_fields=None, skip_required=False):
    """return a dictionary of fields containing name, type, length
    :param input_fc {String}:
            Path or reference to feature class or table.
    :param ignore_fields {Array}:
            Array of strings containing field names to ignore (case sensitive). Default is None
    :param skip_required {Boolean}:
            Boolean to skip required fields or not; Default is False
    :return dictionary of field name: attributes
    """
    l_fields = arcpy.ListFields(input_fc)
    field_dict = dict()

    if ignore_fields is None:
        fields_to_ignore = []
    else:
        fields_to_ignore = ignore_fields

    if skip_required:
        for f in l_fields:
            if f.required:
                fields_to_ignore.append(f.name)

    for field in l_fields:
        if field.name not in fields_to_ignore:
            field_dict[field.name] = {
                "name": field.name,
                "alias": field.aliasName,
                "type": field.type,
                "length": field.length,
                "required": field.required
            }
    return field_dict


def compare_schemas(fc1, fc2):
    """compare the schemas of two tables. Return an array of results.
    :param fc1 {String}:
            Path or reference to feature class or table.
    :param fc2 {String}:
            Path or reference to feature class or table.
    :return array of results (field not found, field same, etc)
    """
    result_arr= []
    field_dict1 = make_field_dict(fc1)
    field_dict2 = make_field_dict(fc2)
    for ifield in sorted(list(set(field_dict1.keys()+field_dict2.keys()))):
        # check name for missing fields first
        if not (field_dict1.has_key(ifield)):
            the_result = " {0} not found in {1}".format(ifield, fc1)
            output_msg(the_result)
            result_arr.append(the_result)
        elif not (field_dict2.has_key(ifield)):
            the_result = " {0} not found in {1}".format(ifield, fc2)
            output_msg(the_result)
            result_arr.append(the_result)
        else:
            # string comparison of name, type and length
            if field_dict1[ifield] == field_dict2[ifield]:
                the_result = " {0} field same in both".format(ifield)
                output_msg(the_result)
                result_arr.append(the_result)
            else:
                field_one_type = field_dict1[ifield]['type']
                field_two_type = field_dict2[ifield]['type']
                field_one_length = field_dict1[ifield]['length']
                field_two_length = field_dict2[ifield]['length']

                the_result = " {0} {1} {2} {3} does not exactly match {4} {5} {6} {7}".format(
                    fc1, ifield, field_one_type, field_one_length, fc2, ifield, field_two_type, field_two_length)
                output_msg(the_result)
                result_arr.append(the_result)

    return result_arr


def export_schema_to_csv(input_fc):
    """Create a csv schema report of all fields in a featureclass,
    to the base directory or user folder.
    :param input_fc {String}:
        path or reference to a featureclass.
    """
    import datetime
    import os
    import csv
    # TODO convert to use csv
    start_time = datetime.datetime.today()
    start_date_string = start_time.strftime('%Y%m%d')
    default_env = arcpy.env.workspace
    fc = input_fc
    delimiter = ','
    # nice to convert reported types to types accepted by add field tool
    type_conversions = {"String": "TEXT", "Float": "FLOAT", "Double": "DOUBLE", "SmallInteger": "SHORT", "Integer": "LONG", "Date": "DATE", "Blob": "BLOB", "Raster": "RASTER", "GUID": "GUID", "TRUE": "True", "FALSE": "False"}

    fc_type = 'Unknown'
    d = arcpy.Describe(fc)
    if hasattr(d, 'shapeType'):
        fc_type = d.shapeType
    elif hasattr(d, 'dataType'):
        fc_type = d.dataType

    try:
        output_msg("Processing: {}".format(fc))
        try:
            desc = arcpy.Describe(fc)
        except:
            raise ValueError("{} not found".format(fc))
        arcpy.env.workspace = fc

        report_dir = get_valid_output_path(desc.Path)

        log_file_name = desc.baseName + "_Field_Report " + start_date_string + ".csv"
        log_file_path = os.path.join(report_dir, log_file_name)
        output_msg("Report file: {0}".format(log_file_path))
        with open(log_file_path, "w") as logFile:
            logFile.write("Type,{}".format(fc_type))
            logFile.write(
                "FieldName,FieldType,FieldPrecision,FieldScale,FieldLength,FieldAlias,isNullable,Required,"
                "FieldDomain,DefaultValue,Editable,BaseName\n")

            try:
                fields = arcpy.ListFields(fc)
                for field in fields:
                    output_msg("Writing {}".format(field.name))
                    logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(
                        field.name,
                        type_conversions[field.type],
                        field.precision,
                        field.scale,
                        field.length,
                        field.aliasName,
                        type_conversions[field.isNullable],
                        type_conversions[field.required],
                        field.domain,
                        field.defaultValue,
                        type_conversions[field.editable],
                        field.baseName))
            except Exception as e:
                output_msg(str(e.args[0]))
                output_msg(arcpy.GetMessages())

    except Exception as e:
        output_msg(str(e.args[0]))
        output_msg(arcpy.GetMessages())
    finally:
        output_msg("Completed")
        arcpy.env.workspace = default_env


def import_schema_to_fc(csv_file, fc_name):
    """convert csv schema from report_fields_to_csv_schema
    to a featureclass"""
    # assume headers as per output from export_schema_to_csv
    # get fc type from csv file line 1
    # load the csv file from line 2 for field info
    # get field list
    # ignore OBJECTID, SHAPE
    fields_to_ignore =["OBJECTID", "FID", "SHAPE", "SHAPE_AREA", "SHAPE.AREA", "SHAPE.STAREA()", "SHAPE_LENGTH", "SHAPE.LEN", "SHAPE.STLENGTH()"]
    # create fc from fc_name
    # add fields from field list
    # arcpy.AddField_management(in_table, field_name, field_type, {field_precision}, {field_scale}, {field_length}, {field_alias}, {field_is_nullable}, {field_is_required}, {field_domain})
    pass
