import arc_utils as au
import arcpy
import os


def write_field_info(fc):
    desc = arcpy.Describe(fc)
    root_path = desc.path
    fc_name = desc.name
    print('getting field info from %s' % fc_name)
    if fc_name.find(".") != -1:
        fc_name = fc_name.split(".")[0]
    table_obj = au.table.TableObj(fc)
    output_path = os.path.join(root_path, fc_name + ".tsv")
    with open(output_path, "w") as output_file:
        output_file.write("\t".join(table_obj.field_dict) + "\n")
        for field in table_obj.field_dict.values():
            output_file.write("\t".join(str(value) for value in field.values()) + "\n")


def write_field_values(fc):
    import csv
    desc = arcpy.Describe(fc)
    root_path = desc.path
    print(root_path)
    fc_name = desc.name
    print('getting field values from %s' % fc_name)
    if fc_name.find(".") != -1:
        fc_name = fc_name.split(".")[0]
    field_value_csv = os.path.join(root_path, fc_name + "_field_values.csv")
    with open(field_value_csv, 'a+') as a:
        csvw = csv.writer(a, lineterminator='\n')
        fco = au.table.TableObj(fc)
        for field in fco.fields2:
            print('writing field values for %s' % field)
            values = [field]
            values.extend(fco.get_field_value_set(field))
            csvw.writerow(values)


def get_featureclass_info(workspace):
    ws = arcpy.env.workspace
    arcpy.env.workspace = workspace
    desc = arcpy.Describe(workspace)
    root_path = workspace
    if not desc.dataType == 'Folder':
        root_path = desc.catalogPath  # path
    for fc in arcpy.ListFeatureClasses():
        fc_path = os.path.join(arcpy.env.workspace, fc)
        # write field info
        write_field_info(fc_path)
        # write field values
        write_field_values(fc_path)
    arcpy.env.workspace = ws


def export_field_sets(layr_list, out_xlsx, ignore_fields=None, use_lyr_alias=True):
    """Export unique field values using the maintained library implementation."""
    return au.table.export_field_sets(
        layr_list,
        out_xlsx,
        ignore_fields=ignore_fields,
        use_lyr_alias=use_lyr_alias,
    )