# function from
# http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//00150000000p000000.htm


def output_msg(msg, severity=0):
    """Outputs to print or to Arc. Useful to include in a tool
    that can be run in Python or in ArcGIS """
    # Adds a Message (in case this is run as a tool)
    # and also prints the message to the screen (standard output)
    #
    print msg

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
