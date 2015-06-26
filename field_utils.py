__AUTHOR__ = 'Grant Herbert'
"""utilities for working with fields"""

def get_field_value_set(inputTable, field, charset='ascii'):
    """Get a list of unique field values given an input table,
       a field name string and an optional charset (default='ascii')
       ascii charset will force encoding with ignore option
        Returns a set"""
    import arcpy
    try:
        valueSet = set() # set to hold unique values
        # use data access search cursor combined with, 'with'
        with arcpy.da.SearchCursor(inputTable, field) as values:
            # iterate through all values returned by Search Cursor
            for value in values:
                # Add value to set. If the value is not present,
                # it will be added. If it is present, the set will not
                # allow duplicates.
                if value[0] is None:
                    #Null value
                    valueSet.add("")
                else:
                    if charset != 'ascii':
                        valueSet.add(value[0])
                    else:
                        #if unicode strings are causing problem, try
                        valueSet.add(value[0].encode('ascii', 'ignore'))
        # return list of values
        return valueSet

    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]


def pprint_fields(table):
    """ pretty print table's fields and their properties """
    def _print(l):
        print("".join(["{:>12}".format(i) for i in l]))

    atts = ['name', 'aliasName', 'type', 'baseName', 'domain',
            'editable', 'isNullable', 'length', 'precision',
            'required', 'scale',]
    _print(atts)

    for f in arcpy.ListFields(table):
        _print(["{:>12}".format(getattr(f, i)) for i in atts])