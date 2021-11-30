from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose
from django.conf import settings

# Error codes.
from data_extraction import myExceptions
from data_extraction.myExceptions import Error, downloadList as errorList
from django.conf import settings

import os
import sys
import requests
import urllib.request
import shutil
import boto3
import botocore

from boto3.s3.transfer import TransferConfig

def downloadWellFile(document):
    print("DOWNLOADING WELL FILE")
    print("WELL: " + document.well.well_name)
    print("DOCUMENT: " + document.document_name)
    # Set Destination Folder.
    wellFolder = document.well.well_name
    report = document.report

    makeDirectory('well_data/',False)

    destinationWell = 'well_data/' + wellFolder + '/'
    makeDirectory(destinationWell, settings.USE_S3)
    makeDirectory(destinationWell, False)

    if report is None:
        destination = destinationWell
    else:
        reportName = report.report_type.type_name
        reportName = reportName.replace("\r\n"," ")
        destination = destinationWell + reportName + '/'
        makeDirectory(destination, settings.USE_S3)

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

    name = cleanName(name)

    fileName = name + fileType

    downloadFile(url, destination, fileName)
    filePath = destination + fileName
    fileSize = getFileSize(filePath)

    result = SaveFileToDatabase(document, name, fileType, destination, fileSize)

    if result == 2:
        myError = errorList[5]
        error = Error(myError.code,myError.description,myError.consolLog)
        print(error.consolLog)
        return error
    elif result == 3: 
        myError = errorList[3]
        error = Error(myError.code,myError.description,myError.consolLog)
        print(error.consolLog)
        return error
    else:
        myError = errorList[0]
        error = Error(myError.code,myError.description,myError.consolLog)
        error.description = error.description + " FileName: " + name
        error.well = document.well.well_name
        error.report = document.report
        return error

def cleanName(name):
    name = name.replace("/","")
    name = name.replace(":","")
    name = name.replace("*","")
    name = name.replace("?","")
    name = name.replace('"',"")
    name = name.replace("<","")
    name = name.replace(">","")
    name = name.replace("|","")

    return name

def SaveFileToDatabase(document, file_name, file_ext, file_location, file_size):
    try:
        file = File.objects.filter(
            file_name = file_name,
            file_ext = file_ext,
            file_location = file_location
        ).first()
        if(file is None):
            file = File.objects.create(
                file_name = file_name,
                file_ext = file_ext,
                file_location = file_location,
                file_size = file_size
            )
        else:
            return 2
            

        document.file = file
        document.status = 2
        document.save()

    except Exception as e:
        print(e)
        return 3

    return 1

def makeDirectory(newFolder, S3):
    if S3:
        try:
            s3 = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            directory_name = newFolder
            s3.put_object(Bucket=bucket_name, Key=(directory_name))
        except Exception as e:
            myError = errorList[1]
            error = Error(myError.code,myError.description,myError.consolLog)
            print(f"Error {error.code}: {error.consolLog}")
    else:
        root_folder = settings.MEDIA_ROOT
        newPath = root_folder + newFolder
        if (not os.path.isdir(newPath)==True):
            try:
                os.mkdir(newPath)
            except Exception as e:
                myError = errorList[1]
                error = Error(myError.code,myError.description,myError.consolLog)
                error.consolLog = error.consolLog + "    New Folder: " + newFolder
                print(f"Error {error.code}: {error.consolLog}")

                return error    

    return True

def downloadFile(fromFilePath, destination, fileName):
    toFilePath = destination + fileName
    root_folder = settings.MEDIA_ROOT
    myPath = root_folder + toFilePath
    if settings.USE_S3:
        # Check if file exists
        if(not os.path.exists(myPath)):
            # Download File
            try:
                with urllib.request.urlopen(fromFilePath) as response, open(myPath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                myError = errorList[4]
                error = Error(myError.code,myError.description,myError.consolLog)
                print(f"Error {error.code}: {error.consolLog}")
                print(e)

                return error

        uploadFileS3(myPath, toFilePath)

    else:
        # Check if file exists
        if(not os.path.exists(myPath)):
            # Download File
            try:
                with urllib.request.urlopen(fromFilePath) as response, open(myPath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                myError = errorList[4]
                error = Error(myError.code,myError.description,myError.consolLog)
                print(f"Error {error.code}: {error.consolLog}")
                print(e)

                return error

def uploadFileS3(myPath, destination):
    #s3 = boto3.resource('s3')
    s3_client=boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    directory_name = destination
    threshold = 1024*25
    config = TransferConfig(multipart_threshold=threshold, max_concurrency=1, multipart_chunksize=threshold, use_threads=True)
    #s3.Bucket(bucket_name).upload_file(myPath, directory_name)
    #s3.meta.client.upload_file(myPath, bucket_name, directory_name,Config=config)
    s3_client.upload_file(myPath, bucket_name, directory_name,Config=config)

def copyToTemp(filePath, tempFolder, fileName):
    if settings.USE_S3:
        # filePath is the s3 key (like a file path)
        # tempPath is the path and file name that will be created inside the temp folder

        s3 = boto3.resource('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        #Check if file exists
        try:
            s3.Object(bucket_name, filePath).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("404")
                return False
            else:
                # Something else has gone wrong.
                raise
        
        #Download File
        makeDirectory(tempFolder, False)
        destination = settings.MEDIA_ROOT + tempFolder + fileName
        s3.Bucket(bucket_name).download_file(filePath, destination)
        return True
    else:
        root_folder = settings.MEDIA_ROOT
        filePath = root_folder + filePath
        tempPath = root_folder + 'temp/' + tempFolder + fileName
        # Check if file exists
        if(not os.path.exists(tempPath)):
            # Copy File
            try:
                shutil.copy(filePath, tempPath)
                return True
            except Exception as e:
                myError = errorList[4]
                error = Error(myError.code,myError.description,myError.consolLog)
                print(f"Error {error.code}: {error.consolLog}")
                print(e)

                return False
        else:
            return False

def deleteDirectory(path, S3):
    if S3:
        try:
            s3 = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            bucket = s3.Bucket(bucket_name)
            prefix = path + '/'
            bucket.objects.filter(Prefix=prefix).delete()
        except Exception as e:
            #myError = errorList[1]
            #error = Error(myError.code,myError.description,myError.consolLog)
            #print(f"Error {error.code}: {error.consolLog}")
            return False
    else:
        root_folder = settings.MEDIA_ROOT
        path = root_folder + path
        if (os.path.isdir(path)):
            try:
                shutil.rmtree(path)
            except OSError as e:
                #myError = errorList[1]
                #error = Error(myError.code,myError.description,myError.consolLog)
                #error.consolLog = error.consolLog + "    Deleted Folder: " + path
                #print(f"Error {error.code}: {error.consolLog}")
                print(e)

                return False    
			
    return True

def deleteFile(path, S3):
    if S3:
        try:
            s3 = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            print(path)
            s3.delete_object(Bucket=bucket_name, Key=path)
        except Exception as e:
            #myError = errorList[1]
            #error = Error(myError.code,myError.description,myError.consolLog)
            #print(f"Error {error.code}: {error.consolLog}")
            print(e)
            return False
    else:
        root_folder = settings.MEDIA_ROOT
        path = root_folder + path
        if (os.path.exists(path)):
            try:
                os.remove(path)
            except OSError as e:
                #myError = errorList[1]
                #error = Error(myError.code,myError.description,myError.consolLog)
                #error.consolLog = error.consolLog + "    Deleted Folder: " + path
                #print(f"Error {error.code}: {error.consolLog}")
                print(e)

                return False    
			
    return True

def zipFiles(name,folder):
    if settings.USE_S3:
        zipPath = name
        zipPathFull = settings.MEDIA_ROOT + zipPath
        folder = settings.MEDIA_ROOT + folder
        shutil.make_archive(zipPathFull, 'zip', folder)

        fileSize = getFileSize(zipPath + '.zip')
        return fileSize
    else:
        zipPath = 'temp/' + name
        zipPathFull = settings.MEDIA_ROOT + zipPath
        folder = settings.MEDIA_ROOT + folder
        shutil.make_archive(zipPathFull, 'zip', folder)

        fileSize = getFileSize(zipPath + '.zip')
        return fileSize

def getFileSize(filePath):
    root_folder = settings.MEDIA_ROOT
    size = os.path.getsize(root_folder + filePath)
    return size