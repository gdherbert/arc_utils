"""utilities for working with tables"""
__AUTHOR__ = 'Grant Herbert'

import arcpy
from arcutils.outpututils import output_msg


def make_field_dict(input_fc):
    """return a dictionary of fields containing name, type, length with the option to skip shape fields

    input_fc {String}:
            Path or reference to feature class or table.
    """
    fields_to_ignore = ["SHAPE", "SHAPE_AREA", "SHAPE.AREA", "SHAPE.STAREA()", "SHAPE_LENGTH", "SHAPE.LEN", "SHAPE.STLENGTH()"]
    l_fields=arcpy.ListFields(input_fc)
    field_dict = dict()
    for field in l_fields:
        if field.name.upper() not in fields_to_ignore:
            # return all strings as UPPER CASE
            field_dict[field.name.upper()] = [field.name, field.type.upper(), field.length]
    return field_dict


def compare_table_schemas(fc1, fc2):
    """compare the schemas of two tables. Return an array of results.

    table1 {String}:
            Path or reference to feature class or table.
    table2 {String}:
            Path or reference to feature class or table.
    """
    error_list= []
    field_dict1 = make_field_dict(fc1)
    field_dict2 = make_field_dict(fc2)
    for ifield in sorted(list(set(field_dict1.keys()+field_dict2.keys()))):
        # check name for missing fields first
        if not (field_dict1.has_key(ifield)):
            the_result = " {0} not found in {1}".format(ifield,fc1)
            output_msg(the_result)
            error_list.append(the_result)
        elif not (field_dict2.has_key(ifield)):
            the_result = " {0} not found in {1}".format(ifield,fc2)
            output_msg(the_result)
            error_list.append(the_result)
        else:
            # string comparison of name, type and length
            if field_dict1[ifield] == field_dict2[ifield]:
                the_result = " {0} field same in both".format(ifield)
                output_msg(the_result)
            else:
                field_one_type = field_dict1[ifield][1]
                field_two_type = field_dict2[ifield][1]
                field_one_length = field_dict1[ifield][2]
                field_two_length = field_dict2[ifield][2]

                the_result = " {0} {1} {2} {3} does not exactly match {4} {5} {6} {7}".format(fc1, ifield, field_one_type, field_one_length, fc2, ifield, field_two_type, field_two_length)
                output_msg(the_result)
                error_list.append(the_result)

    return error_list
