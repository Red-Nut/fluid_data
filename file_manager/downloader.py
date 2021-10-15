from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose
from django.conf import settings

# Error codes.
from data_extraction import myExceptions

import os
import requests
import urllib.request
import shutil

def downloadFile(document):
    # Set Destination Folder.
    wellFolder = document.well.well_name
    report = document.report

    destinationWell = wellFolder + '/'

    if (not os.path.isdir(settings.MEDIA_ROOT + destinationWell)):
        try:
            os.mkdir(settings.MEDIA_ROOT + destinationWell)
        except Exception as e:
            error = myExceptions.downloadList[1]
            error.description = error.description
            error.consolLog = error.consolLog
            print(f"Error {error.code}: {error.consolLog}")

            return error
            #return "Failed to create folder: " + destinationWell

    if report is None:
        destination = destinationWell
    else:
        destination = destinationWell + report.report_type.type_name + '/'
        if (not os.path.isdir(settings.MEDIA_ROOT + destination)):
            try:
                os.mkdir(settings.MEDIA_ROOT + destination)
            except Exception as e:
                error = myExceptions.downloadList[1]
                error.description = error.description + ": " + destination
                error.consolLog = error.consolLog + ": " + destination
                print(f"Error {error.code}: {error.consolLog}")

                return error

    # Download File.
    url = document.url.replace(" ", "%20")
    response = requests.get(url)

    if(response.status_code != 200):
        error = myExceptions.downloadList[2]
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

    try:
        with urllib.request.urlopen(url) as response, open(settings.MEDIA_ROOT + filePath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        error = myExceptions.downloadList[4]
        error.description = error.description + ". Well: " + document.well.well_name + ". Document: " + document.document_name
        error.consolLog = error.consolLog + ". Well: " + document.well.well_name + ". Document: " + document.document_name
        print(f"Error {error.code}: {error.consolLog}")
        print(e)

        return error

    fileSize = os.path.getsize(settings.MEDIA_ROOT + filePath)

    error = myExceptions.downloadList[0]
    error.description = error.description + ". Well: " + document.well.well_name + ". Document: " + document.document_name
    error.consolLog = error.consolLog + ". Well: " + document.well.well_name + ". Document: " + document.document_name
    error.file_name = name
    error.file_ext = fileType
    error.file_location = destination
    error.file_size = fileSize
    return error
    
        
			


