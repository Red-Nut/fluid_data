# Other module imports.
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose

# _______________________________________ GENERIC FUNCTIONS _______________________________________

def ConvertToTrueFalse(str):
    # Takes a string of "Y" / "Yes" or "N" / "No" and converts it to a True or False boolean
    str = str.lower()
    if(str == "y" or str == "yes"):
        return True
    elif(str == "n" or str == "no"): 
        return False
    else:
        print("Error: failure to convert '" + str + "' to Boolean.")
        return False

def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

# _______________________________________ DATABASE FUNCTIONS _______________________________________

def wellExists(name):
    # Checks if the well with the given name exists in the database.
    well = Well.objects.filter(well_name=name).first()
    if (well is None):
        return False
    else:
        return True