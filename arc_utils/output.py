# -*- coding: utf-8 -*-
"""output related utilities
"""
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


def get_valid_output_path(path, return_folder_only=True, make_dir=True, fallback_to_user_folder=True):
    """ return a valid path or empty string if not valid.
    If return_folder_only is True (default) and a gdb is passed as path,
       will return the folder containing gdb.
    If make_dir is True (default), path will be created if it doesn't exist..
    If fallback_to_user_folder is True (default), will fallback to userprofile\documents folder
    path {String}:
        filepath
    return_folder_only {Boolean}:
        returned path must be a folder, not a .gdb
    make_dir {Boolean}:
        make the directory if not exists
    fallback_to_user_folder {Boolean}:
        if path not valid, fallback to userprofile\documents folder (if available)
    :return path or empty string
    """
    def _fallback_user_folder():
        if not fallback_to_user_folder:
            return ''
        user_profile = os.environ.get('USERPROFILE') or os.path.expanduser('~')
        if not user_profile:
            return ''
        docs_dir = os.path.join(user_profile, 'Documents')
        if os.path.isdir(docs_dir):
            return docs_dir
        if os.path.isdir(user_profile):
            return user_profile
        return ''

    try:
        path = os.fspath(path)
    except (TypeError, ValueError):
        return _fallback_user_folder()

    if not path:
        return _fallback_user_folder()

    path = os.path.abspath(os.path.expanduser(path))
    report_dir = path

    if os.path.isdir(path):
        if return_folder_only and path.lower().endswith('.gdb'):
            try:
                report_dir = arcpy.Describe(path).Path
            except Exception:
                return _fallback_user_folder()
    elif make_dir:
        try:
            os.makedirs(path)
            report_dir = path
        except OSError:
            return _fallback_user_folder()
    else:
        return _fallback_user_folder()

    if not os.path.isdir(report_dir):
        return _fallback_user_folder()

    return report_dir


def output_to_file(data, path, filename):
    """send result string to file"""
    path = get_valid_output_path(path)
    if not path:
        raise ValueError("invalid output path")
    output_file = os.path.join(path, filename)
    with open(output_file, "w") as output:
        output.write('{}'.format(data))