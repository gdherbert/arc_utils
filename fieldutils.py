__AUTHOR__ = 'Grant Herbert'
"""utilities for working with fields"""
import arcpy
from arcutils.outpututils import output_msg
from arcutils.outpututils import get_output_path

def list_field_names(inputTable):
    """Returns an array of field names given an input table.

        inputTable{String}:
            Path or reference to feature class or table.
    """
    f_list = []
    for f in arcpy.ListFields(inputTable):
        f_list.append(f.name)

    return f_list


def get_field_value_set(inputTable, field, charset='ascii'):
    """Returns a set of unique field values given an input table,
       a field name string and an optional charset (default='ascii')
       ascii charset will force encoding with ignore option.

        inputTable {String}:
            Path or reference to feature class or table.

        field {String}:
            name of the field to parse

        charset {String}:
            character set to use (default = 'ascii').
            Valid values are those in the Python documentation for string encode.
       """

    try:
        value_set = set() # set to hold unique values
        with arcpy.da.SearchCursor(inputTable, field) as values:
            for value in values:
                if value[0] is None:
                    value_set.add("")
                else:
                    if charset != 'ascii':
                        value_set.add(value[0])
                    else:
                        #if unicode strings are causing problem, try
                        value_set.add(value[0].encode('ascii', 'ignore'))

        return value_set

    except arcpy.ExecuteError:
        output_msg(arcpy.GetMessages(2))
    except Exception as e:
        output_msg(e.args[0])


def pprint_fields(table):
    """ pretty print a table's fields and their properties

        inputTable {String}:
            Path or reference to feature class or table.
    """

    def _print(l):
        print("".join(["{:>12}".format(i) for i in l]))

    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]
    _print(atts)

    for f in arcpy.ListFields(table):
        _print(["{:>12}".format(getattr(f, i)) for i in atts])



def field_report(featureclass):
    """Create a csv report of all fields in a featureclass,
    to the base directory or user folder.

    featureclass {String}:
        path or reference to a featureclass.
    """
    import datetime
    import os

    start_time = datetime.datetime.today()
    start_date_string = start_time.strftime('%Y%m%d')
    default_env = arcpy.env.workspace
    fc = featureclass

    try:
        output_msg("Processing: {}".format(fc))
        try:
            desc = arcpy.Describe(fc)
        except:
            raise ValueError("{} not found".format(fc))
        arcpy.env.workspace = fc

        report_dir = get_output_path(desc.Path)

        log_file_name = desc.baseName + "_Field_Report " + start_date_string + ".csv"
        log_file_path = os.path.join(report_dir, log_file_name)
        output_msg("Report file: {0}".format(log_file_path))
        with open(log_file_path, "w") as logFile:
            logFile.write("{0}\n".format(desc.name))
            logFile.write("FieldName,FieldAlias,BaseName,")
            logFile.write("DefaultValue,FieldType,Required,Editable,isNullable,")
            logFile.write("FieldLength,FieldPrecision,FieldScale,FieldDomain\n")

            try:
                fields = arcpy.ListFields(fc)
                for field in fields:
                    output_msg("Writing {}".format(field.name))
                    logFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(
                         field.name, field.aliasName, field.baseName,
                         field.defaultValue, field.type, field.required,
                         field.editable, field.isNullable, field.length,
                         field.precision, field.scale, field.domain))
            except:
                output_msg(arcpy.GetMessages())

    except:
        output_msg(arcpy.GetMessages())
    finally:
        output_msg("Completed")
        arcpy.env.workspace = default_env