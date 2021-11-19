from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from background_task import background

from data_extraction.models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose, UserFileBucket, FileBucketFiles
from data_extraction.myExceptions import Error, downloadList as errorList
from file_manager.downloader import makeDirectory
from . import downloader

import os
import shutil
from zipfile import ZipFile

#@background(schedule=10)
def prepareFileBucket(bucketId, userId):
    user = User.objects.get(pk=userId)
    userFileBucket = UserFileBucket.objects.get(pk=bucketId)
    userFileBucket.status = 2
    userFileBucket.save()

    # Notify user
    send_mail(
        subject='Fluid Data - Preparing Files for Download',
        message='We are preparing data package ' + userFileBucket.name + ' for you. You can check the progress from your profile page and an email will be sent to you when it is ready for download.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

    # Document List
    fileBucketFiles = FileBucketFiles.objects.filter(bucket=userFileBucket).all()
    documents = []
    for fileBucketfile in fileBucketFiles:
        documents.append(fileBucketfile.document)

    # Download each file
    for document in documents:
        result = downloader.downloadWellFile(document)
        if(result.code != "50000" and result.code != "50004"):
            # Failed, notify users
            print("file not downloaded")
            print(result.code)

    # Create File Bucket
    downloader.makeDirectory('file_buckets/',False)
    

    destination = 'file_buckets/' + userFileBucket.name + '/'
    downloader.makeDirectory(destination, False)
    

    # Copy Files
    for document in documents:
        sPath = document.file.file_location + document.file.file_name + document.file.file_ext
        
        dfolder = destination + document.well.well_name + '/'
        downloader.makeDirectory(dfolder, False)
        
        dName = document.file.file_name + document.file.file_ext

        result = downloader.copyToTemp(sPath, dfolder, dName)

    # Zip Folder
    result = downloader.zipFiles('file_buckets/' + userFileBucket.name,destination)

    if settings.USE_S3:
        downloader.uploadFileS3(settings.MEDIA_ROOT + 'file_buckets/' + userFileBucket.name + '.zip', 'file_buckets/' + userFileBucket.name + '.zip')

    # Update file bucket status
    userFileBucket.status = 3
    userFileBucket.save()

    # Notify user
    send_mail(
        subject='Fluid Data - Files ready Download',
        message='Data package ' + userFileBucket.name + ' is ready for download. Access the files from your profile page.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )