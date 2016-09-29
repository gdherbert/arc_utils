"""output related utilities"""
import arcpy
import os

def output_msg(msg, severity=0):
    """Output msg to print and/or to Arc. Useful to include in a tool
    that can be run in Python or in ArcGIS

    msg{String}:
        message to output.

    severity(integer):
        severity = 0 (none), 1 (warning), 2 (error)
    usage:
        output_msg("message")

    function from http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//00150000000p000000.htm
    """

    # Adds a Message (in case this is run as a tool)
    # and also prints the message to the screen (standard output)
    #
    print(msg)

    # Split the message on \n first, so that if it's multiple lines,
    #  a GPMessage will be added for each line
    try:
        for string in msg.split('\n'):
            # Add appropriate geoprocessing message
            #
            if severity == 0:
                arcpy.AddMessage(string)
            elif severity == 1:
                arcpy.AddWarning(string)
            elif severity == 2:
                arcpy.AddError(string)
    except:
        pass


def get_valid_output_path(path, folder_reqd=True, make_dir=True):
    """ return a valid path for an output, eg a folder path.
    If folder_reqd is True (default) and a gdb is passed as path,
    will drop down to the folder containing gdb.
    If path does not exist and make_dir is True (default)
    folder will be created.
    Otherwise will default to userprofile\documents folder
    """
    report_dir = path
    if os.path.isdir(path):
        if folder_reqd:
            if path.lower().endswith(".gdb"):
                report_dir = arcpy.Describe(path).Path
    elif make_dir:
        os.makedirs(path)
        report_dir = path
    else:
        report_dir = os.environ['USERPROFILE']
        if os.path.exists(report_dir + "\\Documents"):
            report_dir = report_dir + "\\Documents"

    return report_dir