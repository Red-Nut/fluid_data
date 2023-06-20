# Django imports.
from django.conf import settings

# Third party imports.
import os
import requests
import urllib.request
import shutil
import boto3
import botocore
#from boto3.s3.transfer import TransferConfig

# Other module imports.
from data_extraction.functions import CleanStr, CleanURL, GetExtFromFileNameOrPath
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose
from data_extraction.responseCodes import Result, GenerateResult, PrintResultLog, downloadList as resultList

# Logging
import logging
log = logging.getLogger("file_manager")

def makeDirectory(newFolder, S3):
    # Make a new folder on local drive or key on AWS.
    # newFolder: the new folder or key to be create.
    # S3: toggle for S3 key or local folder creation.
    
    if S3:
        # Create new key on AWS server
        try:
            s3 = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            directory_name = newFolder
            s3.put_object(Bucket=bucket_name, Key=(directory_name))
        except Exception as e:
            # Handle Error.
            result = GenerateResult(resultList,1)
            result.consolLog = result.consolLog + "    New Folder: " + newFolder
            result.consolLog = result.consolLog + "    Exception: " + str(e)
            PrintResultLog(result)
            return result
    else:
        # Create folder on local server.
        
        # Create the full path.
        root_folder = settings.MEDIA_ROOT
        newPath = root_folder + newFolder

        # Check if folder already exists.
        if (not os.path.isdir(newPath)==True):
            # Create the folder.
            try:
                os.mkdir(newPath)
            except Exception as e:
                # Handle Error.
                result = GenerateResult(resultList,1)
                result.consolLog = result.consolLog + "    New Folder: " + newFolder
                result.consolLog = result.consolLog + "    Exception: " + str(e)
                PrintResultLog(result)
                print(e)
                return result

    # Success.
    result = GenerateResult(resultList,0)
    return result

def downloadFile(fromFilePath, destination, fileName):
    # Test Connection.
    response = requests.get(fromFilePath)
    if(response.status_code != 200):
        result = GenerateResult(resultList,2)
        result.description = result.description + " Response Code: " + response.status_code
        result.consolLog = result.consolLog + " Response Code: " + response.status_code
        PrintResultLog(result)
        return result

    # Local file path.
    toFilePath = destination + fileName
    root_folder = settings.MEDIA_ROOT
    myPath = root_folder + toFilePath

    # Download File.
    if settings.USE_S3:
        # Check if file exists.
        if(not os.path.exists(myPath)):
            # Download File.
            try:
                with urllib.request.urlopen(fromFilePath) as response, open(myPath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                # Handle Error.
                result = GenerateResult(resultList,4)
                PrintResultLog(result)
                print(e)
                return result

        # Upload to S3.
        bool = uploadFileS3(myPath, toFilePath)
        if not bool:
            # Handle Error.
            result = GenerateResult(resultList,9)
            PrintResultLog(result)
            return result
    else:
        # Check if file exists
        if(not os.path.exists(myPath)):
            # Download File
            try:
                with urllib.request.urlopen(fromFilePath) as response, open(myPath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                # Handle Error.
                result = GenerateResult(resultList,4)
                PrintResultLog(result)
                print(e)
                return result

    # Success.
    result = GenerateResult(resultList,0)
    return result

def uploadFileS3(myPath, destination):
    s3_client=boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    directory_name = destination
    threshold = 1024*25
    try:
        config = boto3.s3.transfer.TransferConfig(multipart_threshold=threshold, max_concurrency=1, multipart_chunksize=threshold, use_threads=True)
        s3_client.upload_file(myPath, bucket_name, directory_name,Config=config)
        
        result = GenerateResult(resultList,0)
        return result
    except:
        result = GenerateResult(resultList,9)
        PrintResultLog(result)
        return result

def deleteDirectory(path, S3):
    # Delete local folder or S3 key.
    # path: the path of the folder or key to be deleted.
    # S3: toggle for S3 key or local folder deletion.

    if S3:
        # Delete S3 key.
        try:
            s3 = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            bucket = s3.Bucket(bucket_name)
            prefix = path + '/'
            bucket.objects.filter(Prefix=prefix).delete()
        except Exception as e:
            # Handle Error.
            result = GenerateResult(resultList,7)
            PrintResultLog(result)
            print(e)
            return result
    else:
        # Delete local folder.

        # Create the full path.
        root_folder = settings.MEDIA_ROOT
        path = root_folder + path
        if (os.path.isdir(path)):
            try:
                shutil.rmtree(path)
            except OSError as e:
                # Handle Error.
                result = GenerateResult(resultList,7)
                PrintResultLog(result)
                print(e)
                return result   

    # Success.	
    result = GenerateResult(resultList,0)
    return result

def deleteFile(path, S3):
    # Delete local file or file on AWS server.
    # path: the path of the file to be deleted.
    # S3: toggle for AWS file or local file deletion.

    if S3:
        # Delete file on AWS server.
        try:
            s3 = boto3.client('s3')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            print(path)
            s3.delete_object(Bucket=bucket_name, Key=path)
        except Exception as e:
            # Handle Error.
            result = GenerateResult(resultList,6)
            PrintResultLog(result)
            print(e)
            return result
    else:
        # Delete local file.

        # Create the full path.
        root_folder = settings.MEDIA_ROOT
        path = root_folder + path
        if (os.path.exists(path)):
            try:
                os.remove(path)
            except OSError as e:
                # Handle Error.
                result = GenerateResult(resultList,6)
                PrintResultLog(result)
                print(e)
                return result 
			
    result = GenerateResult(resultList,0)
    return result

def zipFiles(name,folder):
    # Zip all files in a folder.
    # folder: the path of the folder to be zipped.
    # name: name of the resulting zip file. must NOT have .zip on the end.

    # If using S3, the media root is already the temp folder. 
    if settings.USE_S3:
        zipPath = name
    else:
        zipPath = 'temp/' + name
    
    # Path to new zip file (does not include .zip)
    zipPathFull = settings.MEDIA_ROOT + zipPath
    # Path to folder that is being zipped.
    folder = settings.MEDIA_ROOT + folder

    # Create Zip file.
    try:
        shutil.make_archive(zipPathFull, 'zip', folder)
    except Exception as e:
        # Handle Error.
        result = GenerateResult(resultList,8)
        PrintResultLog(result)
        print(e)
        return result

    # Get the size of the new zip file
    fileSize = getFileSize(zipPath + '.zip')

    # Return a successful result with the fileSize attached.
    result = GenerateResult(resultList,0)
    result.fileSize = fileSize
    return result

def getFileSize(filePath):
    # Get the size of a file at a specified filePath in the media folder.
    root_folder = settings.MEDIA_ROOT
    try:
        size = os.path.getsize(root_folder + filePath)
        return size
    except:
        return None



def copyToTemp(filePath, tempFolder, fileName):
    # Copy a file to the local temp folder
    # filePath: path to the file that is being copied.
    # tempFolder: folder inside the local temp directory that the file is copied to.
    # fileName: the name of the file being copied.

    # tempFolder should have "/" on the end. If not fix it.
    if tempFolder[-1] != '/':
        tempFolder = tempFolder + "/"

    folders = tempFolder.split("/")

    if settings.USE_S3:
        # Copy file from AWS Server
        # filePath is the S3 key (like a file path)
        # tempPath is the path and file name that will be created inside the temp folder
        tempPath = tempFolder + fileName
        s3 = boto3.resource('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        # Check if file exists
        try:
            s3.Object(bucket_name, filePath).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # Handle Error.
                result = GenerateResult(resultList,10)
                result.consolLog = result.consolLog + " Error: 404"
                PrintResultLog(result)
                return result
            else:
                # Handle Error.
                result = GenerateResult(resultList,11)
                result.consolLog = result.consolLog + " Error: 404"
                PrintResultLog(result)
                return result
        
        # Make Folders
        folderPath = ""
        for folder in folders:
            folderPath += folder + '/'
            result = makeDirectory(folderPath, False)
            if result.code != "00000":
                PrintResultLog(result)
                return result

        # Download File
        #dir = makeDirectory(tempFolder, False)
        #if dir.code == "00000":
        destination = settings.MEDIA_ROOT + tempPath
        s3.Bucket(bucket_name).download_file(filePath, destination)
        result = GenerateResult(resultList,0)
        return result
        #else:
            # Handle Error.
            #result = dir
            #return result

    else:
        # Copy file from local server
        # filePath is the local file to be copied
        # tempPath is the path and file name that will be created inside the temp folder
        root_folder = settings.MEDIA_ROOT
        filePath = root_folder + filePath
        tempPath = root_folder + 'temp/' + tempFolder + fileName

        # Check if file exists
        if(not os.path.exists(tempPath)):
            # Copy File
            try:
                shutil.copy(filePath, tempPath)
                result = GenerateResult(resultList,0)
                return result
            except Exception as e:
                # Handle Error.
                result = GenerateResult(resultList,13)
                PrintResultLog(result)
                print(e)
                return result
        else:
            # Handle Error.
            result = GenerateResult(resultList,12)
            PrintResultLog(result)
            return result

def downloadWellFile(document):
    #Make directories for the file to be downloaded. 
    result = MakeDirectoryForFile(document)
    if result.code != "00000":
        return result

    destination = result.destination

    # URL.
    url = CleanURL(document.url)

    # File Type
    fileType = GetExtFromFileNameOrPath(url)

    # Name
    name = CleanStr(document.document_name)
    fileName = name + fileType

    # Download File.    
    result = downloadFile(url, destination, fileName)
    if result.code != "00000":
        return result

    # Get the size of the downloaded file.
    filePath = destination + fileName
    fileSize = getFileSize(filePath)

    # Make database entry for the file.
    result = SaveFileToDatabase(document, name, fileType, destination, fileSize)

    if result.code == "00000":
        result.description = result.description + " FileName: " + name
        result.well = document.well.well_name
        result.report = document.report
    return result

def MakeDirectoryForFile(document):
    # Make local well_data folder.
    result = makeDirectory('well_data/',False)
    if result.code != "00000":
        return result

    # Set Destination Folder.
    wellFolder = document.well.well_name
    destinationWell = 'well_data/' + wellFolder + '/'

    # Make local folder for specific well.
    result = makeDirectory(destinationWell, False)
    if result.code != "00000":
        return result

    # If using AWS S3, make AWS folder.
    result = makeDirectory(destinationWell, settings.USE_S3)
    if result.code != "00000":
        return result
    
    # Update destination of the file is part of a report.
    report = document.report
    if report is None:
        destination = destinationWell
    else:
        # Update destination
        reportName = CleanStr(report.report_type.type_name)
        destination = destinationWell + reportName + '/'

        # Make local folder for specific well.
        result = makeDirectory(destination, False)
        if result.code != "00000":
            return result
        # If using AWS S3, make AWS folder.
        result = makeDirectory(destination, settings.USE_S3)
        if result.code != "00000":
            return result

    result = GenerateResult(resultList,0)
    result.destination = destination
    return result

def SaveFileToDatabase(document, file_name, file_ext, file_location, file_size):
    try:
        # Check if the file object exists.
        file = File.objects.filter(
            file_name = file_name,
            file_ext = file_ext,
            file_location = file_location
        ).first()

        if(file is None):
            # Create the file object.
            file = File.objects.create(
                file_name = file_name,
                file_ext = file_ext,
                file_location = file_location,
                file_size = file_size
            )
        else:
            # If file already exists - Handle Error.
            result = GenerateResult(resultList,5)
            PrintResultLog(result)
            #return result
            
        # Save the new file entry.
        document.file = file
        # Update the document file status.
        document.status = 2
        document.save()

    except Exception as e:
        if hasattr(e, 'message'):
            # Handle Error
            result = GenerateResult(resultList,3)
            result.consolLog = result.consolLog + ". Message: " + e.message
            log.error(result.consolLog)
            return result
        else:
            # Handle Error
            result = GenerateResult(resultList,3)
            log.error(result.consolLog)
            return result

    # Success.
    result = GenerateResult(resultList,0)
    return result












