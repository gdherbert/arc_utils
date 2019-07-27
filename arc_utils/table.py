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
        self.describe_obj = self._describe_object()
        self.name = self._get_fc_name()
        self.type = self._get_fc_type()
        self.fields = self._list_field_names()
        self.fields2 = self._list_field_names(required=False)
        self.field_dict = self._make_field_dict()

    def _describe_object(self):
        """ returns describe object"""
        return arcpy.Describe(self.path)

    def _get_fc_name(self):
        return self.describe_obj.baseName

    def _get_fc_type(self):
        if hasattr(self.describe_obj, 'shapeType'):
            return self.describe_obj.shapeType
        elif hasattr(self.describe_obj, 'dataType'):
            return self.describe_obj.dataType
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
        all properties exposed by the arcpy.ListFields tool
        """
        field_dict = dict()
        for field in arcpy.ListFields(self.path):
            field_dict[field.name] = {
                "name": field.name,
                "baseName": field.baseName,
                "aliasName": field.aliasName,
                "type": field.type,
                "length": field.length,
                "required": field.required,
                "domain": field.domain,
                "defaultValue": field.defaultValue,
                "precision": field.precision,
                "scale": field.scale,
                "isNullable": field.isNullable,
                "editable": field.editable
            }
        return field_dict

    def get_field_info_as_text(self, sep="\t"):
        """ Create a delimeter separated output of a table's fields and their properties
            :param sep {String}
                Separator value to use. eg r"\t" for tab (default), "," for comma
            :return string of values with separator between
        """
        str_output = sep.join("{}\n".format(self.field_dict.keys()))
        for k in self.field_dict.keys():
            str_output += self.field_dict[k] + sep
        str_output += "\n"
        return str_output

    def get_max_field_value(self, field, lengthcomp=False):
        """Return the largest value (if numeric).
        lexicographic string comparison is used to determine largest value for strings by default.
            :param {String} field:
            name of the field to parse
            :param {Boolean} lengthcomp:
            If True will compare strings for length rather than lexicographically (ascii value of letters)
        """
        field_type = self.field_dict[field]['type']
        if field_type in ["Geometry"]:
            print("Cannot process Geometry field")
            return None
        elif field_type in ["String"]:
            result = ''
        else:
            result = 0
        with arcpy.da.SearchCursor(self.path, field) as values:
            for value in values:
                if value[0] is not None:
                    val = value[0]
                    if field_type in ["String"] and lengthcomp:
                        if len(val) > len(result):
                            result = val
                    else:
                        if val > result:
                            result = val
        return result

    def get_max_field_value_length(self, field):
        """Return the length of the maximum value in the field.
            :param: field {String}:
            name of the field to parse
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

    def get_multiple_field_value_set(self, fields, sep=':'):
        """return a set of unique field values for an input table
        and any number of fields (values will be concatenated with sep)
        null values converted to 'NULL'
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
        data = arcpy.da.TableToNumPyArray(self.path, fieldslist, null_value='NULL')
        df = pandas.DataFrame(data)
        pandas.DataFrame.drop_duplicates(df, inplace=True)
        # concatenate values
        if len(fieldslist) > 1:
            result = df[fieldslist].apply(lambda x: sep.join(x.dropna().astype(str)), axis=1)  # all types
        else:
            result = df.values.flatten()
        # return as a set
        return set(result)

    def find_duplicate_field_values(self, field, charset='ascii'):
        """Return set of unique field values
            :param field {String}:
                name of the field to parse
            :param: charset {String}:
                character set to use (default = 'ascii').
                Valid values are those in the Python documentation for string encode.
            :return set of values which are duplicated in the field (ignores Null values).
           """
        try:
            dup_set = set()  # set to hold duplicate values
            value_set = set()  # set to hold unique values
            with arcpy.da.SearchCursor(self.path, field) as values:
                for value in values:
                    if value[0] in value_set:
                        dup_set.add(value[0])
                    if isinstance(value[0], (str, unicode)):
                        if charset != 'ascii':
                            value_set.add(value[0])
                        else:
                            # if unicode strings are causing problem, try
                            value_set.add(value[0].encode('ascii', 'ignore'))
                    else:
                        value_set.add(value[0])
            return dup_set

        except arcpy.ExecuteError:
            output_msg(arcpy.GetMessages(2))
        except Exception as e:
            output_msg(e.args[0])

    def export_schema_to_csv(self, path):
        """Create a csv schema report of all fields in a featureclass,
        to the supplied path.
        """
        import datetime
        import os
        import csv
        # TODO convert to use csv
        start_time = datetime.datetime.today()
        start_date_string = start_time.strftime('%Y%m%d')
        default_env = arcpy.env.workspace
        fc = self.path
        delimiter = ','
        # nice to convert reported types to types accepted by add field tool
        type_conversions = {"String": "TEXT", "Float": "FLOAT", "Double": "DOUBLE", "SmallInteger": "SHORT",
                            "Integer": "LONG", "Date": "DATE", "Blob": "BLOB", "Raster": "RASTER", "GUID": "GUID",
                            "TRUE": "True", "FALSE": "False"}

        output_msg("Processing: {}".format(self.path))

        try:
            fc_type = self.type

            report_dir = get_valid_output_path(path)
            out_file_name = self.name + "_Field_Report " + start_date_string + ".csv"
            out_file_path = os.path.join(report_dir, out_file_name)
            output_msg("Report file: {0}".format(out_file_path))
            with open(out_file_path, "w") as logFile:
                logFile.write("Type,{}".format(fc_type))
                logFile.write(
                    "FieldName,FieldType,FieldPrecision,FieldScale,FieldLength,FieldAlias,isNullable,Required,"
                    "FieldDomain,DefaultValue,Editable,BaseName\n")

                for field in self.field_dict:
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
                        field.baseName)
                    )

            return out_file_path
        except Exception as e:
            output_msg(str(e.args[0]))
            output_msg(arcpy.GetMessages())

    def compare_field_values_to_domain(self, field, gdb, domain_name):
        """compare field values with domain values
            return a named tuple (matched = values in domain,
            unmatched = values outside of domain
            :param field {string}
                Field name
            :param gdb {string}
                Geodatabase path
            :param domain_name {string}
                Domain name in gdb
        """
        from collections import namedtuple
        nt = namedtuple('Result', 'match unmatched')
        field_values = self.get_field_value_set(field)
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
            # compare upper and lower bounds
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


def get_max_field_value(input_fc, field, treatasfloat=False):
    """Return either the longest string in the field,
    or the largest number.
        :param input_fc {String}:
            Path or reference to feature class or table.
        :param field {String}:
            name of the field to parse
        :param treatasfloat:
            setting to treat the field as a float value (expects all numeric)
        :return value of largest field entry
    """
    result = None
    with arcpy.da.SearchCursor(input_fc, field) as values:
            for value in values:
                if value[0] is not None:
                    if treatasfloat:
                        val = float(value[0])
                    else:
                        val = value[0]
                    if isinstance(val, (str, unicode)):
                        # return longest string
                        if result is None:
                            result = ''
                        if len(val) > len(result):
                            result = val
                    else:
                        if result is None:
                            result = 0
                        if val > result:
                            result = val
    return result


def compare_schema(fc1, fc2):
    """compare the schemas of two tables. Return an array of results.
    :param fc1 {String}:
            Path or reference to feature class or table.
    :param fc2 {String}:
            Path or reference to feature class or table.
    :return array of results (field not found, field same, etc)
    """
    result_arr= []
    fcobj1 = TableObj(fc1)
    fcobj2 = TableObj(fc2)
    field_dict1 = fcobj1.field_dict
    field_dict2 = fcobj2.field_dict
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
