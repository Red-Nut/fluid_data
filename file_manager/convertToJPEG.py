# Django imports.
from django.conf import settings

# Third party imports.
import os
import math
from PIL import Image #pip install Pillow
from pdf2image import convert_from_path, pdfinfo_from_path #pip install pdf2image and install poppler and add to PATH (https://pypi.org/project/pdf2image/)
import tempfile

# This module imports.
from .fileModule import deleteDirectory, deleteFile, makeDirectory, copyToTemp, uploadFileS3, getFileSize

# Other module imports.
from data_extraction.responseCodes import Result, GenerateResult, PrintResultLog, convertList as resultList
from data_extraction.models import Company, Data, Document, File, Page, Report, State, WellStatus, Well


def convertFile(document):
    # Converts the file accociated with this document to a series of PNG files, one for each page.
    # Currently available for TIFF and PDF files.

    path = document.file.file_location + document.file.file_name + document.file.file_ext

    # Check if already converted.    
    if not document.converted:
        # Handle Error
        result = GenerateResult(resultList,2)
        result.description = result.description + ": " + path
        result.consolLog = result.consolLog + ": " + path
        PrintResultLog(result)
        return result
    else:
        if document.file.file_location[:9] == "well_data":
            imageFolder1 = "file_images" + document.file.file_location[9-len(document.file.file_location):]
            imageFolder = imageFolder1 + document.file.file_name + '/'
        else:
            print("document in wrong location")

        # Download file to temp directory:
        if settings.USE_S3:
            AWSpath = document.file.file_location + document.file.file_name + document.file.file_ext
            fileName = document.file.file_name + document.file.file_ext

            result = makeDirectory("well_data" + '/', False)
            if result.code != "00000":
                return result

            result = makeDirectory("well_data" + '/' + document.well.well_name + '/', False)
            if result.code != "00000":
                return result
            
            result = makeDirectory(document.file.file_location, False)
            if result.code != "00000":
                return result

            result = copyToTemp(AWSpath, document.file.file_location, fileName)
            if result.code != "00000":
                return result

            # Create working directory:
            result = makeDirectory("file_images" + '/', False)
            if result.code != "00000":
                return result

            result = makeDirectory("file_images" + '/' + document.well.well_name, False)
            if result.code != "00000":
                return result

            result = makeDirectory(imageFolder1, False)
            if result.code != "00000":
                return result

            result = makeDirectory(imageFolder, False)
            if result.code != "00000":
                return result

        # Create image directory
        result = makeDirectory("file_images/", settings.USE_S3)
        if result.code != "00000":
            return result

        result = makeDirectory("file_images" + '/' + document.well.well_name + '/', settings.USE_S3)
        if result.code != "00000":
            return result

        result = makeDirectory(imageFolder1, settings.USE_S3)
        if result.code != "00000":
            return result

        result = makeDirectory(imageFolder, settings.USE_S3)
        if result.code != "00000":
            return result

    
        # Check it is a format that can be converted.
        if document.file.file_ext == ".tiff" or document.file.file_ext == ".tif" or document.file.file_ext == ".pdf":
            # Convert if TIF file.
            if document.file.file_ext == ".tiff" or document.file.file_ext == ".tif":
                result = convertTIFF(path,imageFolder,document)
            # Convert if PDF file.  
            elif document.file.file_ext == ".pdf":
                result = convertPDF(path,imageFolder,document)

            # Check for conversion success.
            if result.code == "00000":
                # Update document converted status
                document.converted = True
                document.save()

                # Delete temporary files:
                if settings.USE_S3:
                    result1 = deleteFile(path, False)
                    if result1.code != "00000":
                        return result1

                    result1 = deleteDirectory(imageFolder, False)
                    if result1.code != "00000":
                        return result1

            # Return result.
            return result

        # If not a TIF or PDF file
        else:
            # Handle Error
            result = GenerateResult(resultList,1)
            result.description = result.description + ": " + path
            result.consolLog = result.consolLog + ": " + path
            PrintResultLog(result)
            return result

def convertTIFF(path,folder,document):
    fullPath = settings.MEDIA_ROOT + path
    folderPath = settings.MEDIA_ROOT + folder

    try:
        #open tif
        im = Image.open(fullPath)

        #create directory
        result = makeDirectory(folder, False)
        if result.code != "00000":
            return result

        #loop through pages
        for i in range(1000):
            if(i == 999):
                # Handle Error
                result = GenerateResult(resultList,13)
                result.description = result.description + path
                PrintResultLog(result)
                return result
            try:
                #load page
                im.seek(i)
                fileName = "page" + str(i+1) + ".jpg"
                filePath = folderPath + fileName
                #file_location = document.file.file_location + document.file.file_name

                try:
                    im.thumbnail(im.size)
                    im.save(filePath, "JPEG", quality=100)

                    fileSize = getFileSize(folder + fileName)

                    result = uploadFileS3(filePath, folder + fileName)
                    if result.code != "00000":
                        return result

                    try:
                        fileObject = File.objects.create(
                            file_name = "page" + str(i+1),
                            file_ext = "jpg",
                            file_location = folder,
                            file_size = fileSize
                        )
                        fileObject.save()

                    except Exception as e:
                        # Handle Error
                        result = GenerateResult(resultList,5)
                        result.description = result.description + str(e)
                        PrintResultLog(result)
                        return result
                    try:
                        page = Page.objects.create(
                            document=document, 
                            page_no = i+1,
                            file = fileObject,
                            extracted = False,
                        )
                        page.save()
                    except Exception as e:
                        # Handle Error
                        result = GenerateResult(resultList,4)
                        result.description = result.description + str(e)
                        PrintResultLog(result)
                        print(e)
                        return result

                except Exception as e:
                    # Handle Error
                    result = GenerateResult(resultList,10)
                    result.description = result.description + str(e)
                    print(e)
                    PrintResultLog(result)
                    return result
            except:
                # End of file
                break

    except Exception as e:
        # Handle Error
        result = GenerateResult(resultList,10)
        result.description = result.description + str(e)
        PrintResultLog(result)
        return result

    # Return Success
    result = GenerateResult(resultList,0)
    return result

def convertPDF(path,folder,document):
    fullPath = settings.MEDIA_ROOT + path
    folderPath = settings.MEDIA_ROOT + folder

    try:
        with tempfile.TemporaryDirectory() as tempPath:
            #create pages
            try:
                pages = convert_from_path(fullPath, output_folder=tempPath)
                info = pdfinfo_from_path(fullPath, userpw=None, poppler_path=None)
                maxPages = info["Pages"]
            except Exception as e:
                # Handle Error
                result = GenerateResult(resultList,14)
                result.consolLog = result.consolLog + str(e)
                PrintResultLog(result)
                return result

            #create directory
            result = makeDirectory(folder, False)
            if result.code != "00000":
                return result

            #save pages
            try:
                for x in range(1, maxPages+1, 10) : 
                    try:
                        pages = convert_from_path(fullPath, dpi=200, output_folder=tempPath, first_page=x, last_page = min(x+10-1,maxPages))
                    except Exception as e:
                        # Handle Error
                        result = GenerateResult(resultList,14)
                        result.consolLog = result.consolLog + str(e)
                        PrintResultLog(result)
                        return result

                    for y in range(0, len(pages)):
                        i = x + y - 1
                        fileName = "page" + str(i+1) + ".jpg"
                        filePath = folderPath + fileName

                        try:
                            pages[y].save(filePath, 'JPEG')
                        except Exception as e:
                            # Handle Error
                            result = GenerateResult(resultList,7)
                            result.consolLog = result.consolLog + str(e)
                            PrintResultLog(result)
                            print(e)
                            return result

                        fileSize = getFileSize(folder + fileName)
                        if fileSize is None:
                            # Handle Error
                            result = GenerateResult(resultList,4)
                            PrintResultLog(result)
                            return result
                        
                        result = uploadFileS3(filePath, folder + fileName)
                        if result.code != "00000":
                            return result

                        try:
                            pass
                            # Save the file object to the database.
                            fileObject = File.objects.create(
                                file_name = "page" + str(i+1),
                                file_ext = "jpg",
                                file_location = folder,
                                file_size = fileSize
                            )

                        except Exception as e:
                            # Handle Error
                            result = GenerateResult(resultList,5)
                            result.description = result.description + str(e)
                            PrintResultLog(result)
                            return result
                        try:
                            pass
                            # Save the page object to the database.
                            page = Page.objects.create(
                                document=document, 
                                page_no = i+1,
                                file = fileObject,
                                extracted = False,
                            )
                        except Exception as e:
                            # Handle Error
                            result = GenerateResult(resultList,6)
                            result.code = result.code + str(e)
                            result.description = result.description + str(e)
                            PrintResultLog(result)
                            return result

            except Exception as e:
                # Handle Error
                result = GenerateResult(resultList,4)
                result.code = result.code + str(e)
                result.description = result.description + str(e)
                PrintResultLog(result)
                return result
    except Exception as e:
        # Handle Error
        result = GenerateResult(resultList,11)
        result.description = result.description + str(e)
        PrintResultLog(result)
        return result

    # Return Success.
    result = GenerateResult(resultList,0)
    return result