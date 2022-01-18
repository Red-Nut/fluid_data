# Django imports.
from django.conf import settings

# Third party imports.
import json

# Other module imports.
from .models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose, UserFileBucket, FileBucketFiles

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

def CleanStr(str):
    str = str.replace("/","")
    str = str.replace(":","")
    str = str.replace("*","")
    str = str.replace("?","")
    str = str.replace('"',"")
    str = str.replace("<","")
    str = str.replace(">","")
    str = str.replace("|","")
    str = str.replace("\r\n"," ")

    return str

def CleanURL(str):
    str = str.replace(" ", "%20")
    return str

def GetExtFromFileNameOrPath(str):
    x = len(str) - str.rfind('.')
    ext = str[-x:]
    return ext

def NumberToText(value):
    return ("{:,}".format(value))

# _______________________________________ APP FUNCTIONS _______________________________________
def fileSizeAsText(size):
	if(size<=99):
		text = round(size,0)
		text = str(text) + " byte"
	elif(size > 1000*1000):
		text = round(size/1000/1000,2)
		text = str(text) + " Mb"
	else:
		text = round(size/1000,2)
		text = str(text) + " kb"

	return text

def GetDocumentExt(document):
    if(document.file is None):
        x = len(document.url) - document.url.rfind('.')
        ext = document.url.lower()[-x:]
    else:
        ext = document.file.file_ext

    return ext

def GetDocumentLink(document):
    if(document.file is None):
        link = None
    else:
        link = settings.MEDIA_URL + 'well_data/' + document.file.file_location + document.file.file_name + '.' + document.file.file_ext.replace(".","")

    return link

class ResultEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

# _______________________________________ DATABASE FUNCTIONS _______________________________________

def wellExists(name):
    # Checks if the well with the given name exists in the database.
    well = Well.objects.filter(well_name=name).first()
    if (well is None):
        return False
    else:
        return True

def getDocumentTextAsPagesObject(document):
	pageObjects = Page.objects.filter(document=document).order_by("page_no")

	pages = []
	for pageObject in pageObjects:
		texts = Text.objects.filter(
				page = pageObject
			).order_by(
				"BoundingPolys__y", "BoundingPolys__x"
			).all()

		page = {page:pageObject,texts:texts}

		pages.append(page)

	return pages


