from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose
from django.conf import settings

# Error codes.
from data_extraction import myExceptions
from data_extraction.myExceptions import Error, downloadList as errorList

import os
import requests
import urllib.request
import shutil

def downloadWellFile(document):
    # Set Destination Folder.
    wellFolder = document.well.well_name
    report = document.report

    destinationWell = wellFolder + '/'
    root_folder = settings.MEDIA_ROOT + 'well_data/'

    if (not os.path.isdir(root_folder + destinationWell)):
        try:
            os.mkdir(root_folder + destinationWell)
        except Exception as e:
            myError = errorList[1]
            error = Error(myError.code,myError.description,myError.consolLog)
            print(f"Error {error.code}: {error.consolLog}")

            return error
            #return "Failed to create folder: " + destinationWell

    if report is None:
        destination = destinationWell
    else:
        destination = destinationWell + report.report_type.type_name + '/'
        if (not os.path.isdir(root_folder + destination)):
            try:
                os.mkdir(root_folder + destination)
            except Exception as e:
                myError = errorList[1]
                error = Error(myError.code,myError.description,myError.consolLog)
                error.description = error.description + ": " + destination
                error.consolLog = error.consolLog + ": " + destination
                print(f"Error {error.code}: {error.consolLog}")

                return error

    # Download File.
    url = document.url.replace(" ", "%20")
    response = requests.get(url)

    if(response.status_code != 200):
        myError = errorList[2]
        error = Error(myError.code,myError.description,myError.consolLog)
        error.description = error.description + " Response Code: " + response.status_code
        error.consolLog = error.consolLog + " Response Code: " + response.status_code
        print(f"Error {error.code}: {error.consolLog}")

        return error

    x = len(url) - url.rfind('.')
    fileType = url[-x:]

    name = document.document_name

    name = name.replace("/","")
    name = name.replace(":","")
    name = name.replace("*","")
    name = name.replace("?","")
    name = name.replace('"',"")
    name = name.replace("<","")
    name = name.replace(">","")
    name = name.replace("|","")

    filePath = destination + name + fileType

    # Check if file exists
    if(not os.path.exists(root_folder + filePath)):
        try:
            with urllib.request.urlopen(url) as response, open(root_folder + filePath, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except Exception as e:
            myError = errorList[4]
            error = Error(myError.code,myError.description,myError.consolLog)
            error.description = error.description + ". Well: " + document.well.well_name + ". Document: " + document.document_name
            error.consolLog = error.consolLog + ". Well: " + document.well.well_name + ". Document: " + document.document_name
            print(f"Error {error.code}: {error.consolLog}")
            print(e)

        return error

    fileSize = os.path.getsize(root_folder + filePath)

    myError = errorList[0]
    error = Error(myError.code,myError.description,myError.consolLog)
    error.description = error.description + " FileName: " + name
    error.well = document.well.well_name
    error.report = document.report
    error.file_name = name
    error.file_ext = fileType
    error.file_location = destination
    error.file_size = fileSize
    return error
    
        
			


