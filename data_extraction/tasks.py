import logging
import time
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .celery import app
 
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from .models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose, UserFileBucket, FileBucketFiles
from file_manager import downloader, convertToJPEG, fileBucket
 
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
        if(document.status != 2):
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
    zipSize = downloader.zipFiles('file_buckets/' + userFileBucket.name,destination)

    if settings.USE_S3:
        downloader.uploadFileS3(settings.MEDIA_ROOT + 'file_buckets/' + userFileBucket.name + '.zip', 'file_buckets/' + userFileBucket.name + '.zip')

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
    downloader.deleteFile(filePath, useS3)

def emptyFileBucket(user):
	fileBucket = UserFileBucket.objects.filter(user=user).first()

	if(fileBucket is not None):
		files = FileBucketFiles.objects.filter(bucket=fileBucket).all()
		for file in files:
			file.delete()

	return True