# Django imports.
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

# Third party imports.
import logging
import time
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .celery import app

# This module imports.
from data_extraction.models import *

# Other module imports.
from file_manager import fileModule, convertToJPEG, fileBuckets
from administration import views as admin_views
from interpretation.views import ExtractTextFromDocument, RunPageTextAutomation
 
@app.task
def ProcessDocument(documentId):
    document = Document.objects.get(id=documentId)
     # Download Document
    if(document.status != 2):
        #print("Document Status: " + document.get_status_display())
        result = fileModule.downloadWellFile(document)
        if(result.code != "50000" and result.code != "50004"):
            # Failed, notify users
            print("file not downloaded")
            print(result.code)

            return

    # Extract Text from document
    result = ExtractTextFromDocument(documentId, 1, 99)

    # Extract Data from text
    dataTypes = DataType.objects.all()

    for dataType in dataTypes:
        result = RunPageTextAutomation(documentId, dataType)

@app.task
def saveFileBucket(userId):
    user = User.objects.get(pk=userId)
    unsaved = UserFileBucket.objects.filter(user=user).first()

    # Create new bucket.
    user = User.objects.get(pk=userId)
    userFileBucket = UserFileBucket.objects.create(user=user)
    name = user.first_name + user.last_name + str(userFileBucket.id)
    userFileBucket.name = name
    userFileBucket.status = 2
    userFileBucket.save()

    # Copy files from temporary bucket.
    documents = FileBucketFiles.objects.filter(bucket=unsaved).all()
    for document in documents:
        FileBucketFiles.objects.create(bucket=userFileBucket, document=document.document)

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

    # Empty temporary bucket.
    emptyFileBucket(user)

    # Download each file
    for document in documents:
        print("Document Name: " + document.document_name)
        if(document.status != 2):

            print("Document Status: " + document.get_status_display())
            result = fileModule.downloadWellFile(document)
            if(result.code != "50000" and result.code != "50004"):
                # Failed, notify users
                print("file not downloaded")
                print(result.code)

    # Create File Bucket
    fileModule.makeDirectory('file_buckets/',False)
    

    destination = 'file_buckets/' + userFileBucket.name + '/'
    fileModule.makeDirectory(destination, False)
    

    # Copy Files
    for document in documents:
        if document.file is not None:
            sPath = document.file.file_location + document.file.file_name + document.file.file_ext
            
            dfolder = destination + document.well.well_name + '/'
            fileModule.makeDirectory(dfolder, False)
            
            dName = document.file.file_name + document.file.file_ext

            result = fileModule.copyToTemp(sPath, dfolder, dName)

    # Zip Folder
    result = fileModule.zipFiles('file_buckets/' + userFileBucket.name,destination)
    if result.code != "00000":
        return result

    zipSize = result.fileSize

    if settings.USE_S3:
        fileModule.uploadFileS3(settings.MEDIA_ROOT + 'file_buckets/' + userFileBucket.name + '.zip', 'file_buckets/' + userFileBucket.name + '.zip')

    # Update file bucket status
    userFileBucket.status = 3
    userFileBucket.zipSize = zipSize
    userFileBucket.save()

    # Notify user
    send_mail(
        subject='Fluid Data - Files ready Download',
        message='Data package ' + userFileBucket.name + ' is ready for download. Access the files from your profile page. Or using this link: ' + settings.MEDIA_URL + "file_buckets/" + userFileBucket.name + ".zip",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )


@app.task
def deleteFileBucket(filePath, useS3):
    fileModule.deleteFile(filePath, useS3)

def emptyFileBucket(user):
	fileBucket = UserFileBucket.objects.filter(user=user).first()

	if(fileBucket is not None):
		files = FileBucketFiles.objects.filter(bucket=fileBucket).all()
		for file in files:
			file.delete()

	return True

@app.task
def UpdateCompanyNames():
    admin_views.UpdateCompanyNamesTask()

    return