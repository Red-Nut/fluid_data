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
 
# Logging
import logging
log = logging.getLogger("celery_tasks")

@app.task
def ProcessDocument(documentId):
    success = True
    document = Document.objects.get(id=documentId)

    log.info(f"({document.id}) Begin processing document. Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")

     # Download Document
    if(document.status != document.DOWNLOADED and document.status != document.IGNORED):
        #log.debug(f"({document.id}) Downloading document. Document: {document.id}, Status: {document.get_status_display()}")
        result = fileModule.downloadWellFile(document)
        if(result.code != "00000"):
            # Failed, notify users
            log.error(f"({document.id}) Document not downloaded. Document: {document.id}, Error {result.code}: {result.description}")
            success = False
            return

    # Extract Text from document
    if document.conversion_status != document.IGNORED:
        #log.debug(f"({document.id}) Extract Text from document. Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")
        result = ExtractTextFromDocument(documentId, 1, 99)
        if(result.code != "00000"):
            log.error(f"({document.id}) Error {result.code}: {result.description}. While extracting images/text from Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")
            success = False

    # Extract Data from text
    if document.conversion_status == document.CONVERTED:
        #log.debug(f"({document.id}) Extract Data from document. Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")
        dataTypes = DataType.objects.all()
        for dataType in dataTypes:
            result = RunPageTextAutomation(documentId, dataType)
            if(result != True):
                log.error(f"({document.id}) Error while extracting data from Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")
                success = False
                return

    if success:
        log.info(f"Success ({document.id}) Completed processing document. Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")
    else:
        log.info(f"Failed ({document.id}) to process document. Well: {document.well.well_name} ({document.well.id}), Document: {document.document_name} ({document.id})")
        
    
    return

@app.task
def saveFileBucket(userId):
    try:
        user = User.objects.get(pk=userId)
        unsaved = UserFileBucket.objects.filter(user=user).first() # first bucket is always used as temporary bucket
        log.info('Saving File Bucket: %i for user: %s.', unsaved.id, user.username)

        # Create new bucket.
        userFileBucket = UserFileBucket.objects.create(
            user=user
            name = 'tempName'
            status = unsaved.PREPARING
        )
        name = user.first_name + user.last_name + str(userFileBucket.id)
        userFileBucket.name = name
        userFileBucket.save()

        # Copy files from temporary bucket.
        documents = FileBucketFiles.objects.filter(bucket=unsaved).all()
        for document in documents:
            FileBucketFiles.objects.create(bucket=userFileBucket, document=document.document)

        # Notify user
        try:
            send_mail(
                subject='Fluid Data - Preparing Files for Download',
                message='We are preparing data package ' + userFileBucket.name + ' for you. You can check the progress from your profile page and an email will be sent to you when it is ready for download.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            log.info('Email sent to user: %s. Preparing file bucket: %i', user.username, userFileBucket.id)
        except:
            log.error('Failed to send email to user: %s. Preparing file bucket: %i', user.username, userFileBucket.id)

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
                log.debug('Downloading document (%i) for file bucket (%i).', document.id, userFileBucket.id)
                result = fileModule.downloadWellFile(document)
                if(result.code != "50000" and result.code != "50004"):
                    # Failed, notify users
                    log.debug('File bucket (%i) document (%i) not downloaded. Error %s: %s', userFileBucket.id, document.id, result.code, result.consolLog)

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
        log.debug('Zipping Folder for file bucket (%i).', userFileBucket.id)
        result = fileModule.zipFiles('file_buckets/' + userFileBucket.name,destination)
        if result.code != "00000":
            log.error('Failed to zip file bucket %i', userFileBucket.id)
            return result

        zipSize = result.fileSize

        if settings.USE_S3:
            fileModule.uploadFileS3(settings.MEDIA_ROOT + 'file_buckets/' + userFileBucket.name + '.zip', 'file_buckets/' + userFileBucket.name + '.zip')

        # Update file bucket status
        userFileBucket.status = userFileBucket.READY
        userFileBucket.zipSize = zipSize
        userFileBucket.save()

        # Notify user
        try:
            send_mail(
                subject='Fluid Data - Files ready Download',
                message='Data package ' + userFileBucket.name + ' is ready for download. Access the files from your profile page. Or using this link: ' + settings.MEDIA_URL + "file_buckets/" + userFileBucket.name + ".zip",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            log.info('Email sent to user: %s. Finished preparing bucket: %i', user.username, unsaved.id)
        except:
            log.error('Failed to send email to user: %s. Finished preparing bucket: %i', user.username, userFileBucket.id)
    except:
        log.error('An unknown error occured whil saving file bucket: %i for user: %s.', unsaved.id, user.username)
    return


@app.task
def deleteFileBucket(filePath, useS3):
    log.info('Deleting files in path: %s.', filePath)
    fileModule.deleteFile(filePath, useS3)
    return

def emptyFileBucket(user):
    log.info('Emptying file bucket for user: %s.', user)
    fileBucket = UserFileBucket.objects.filter(user=user).first()

    if(fileBucket is not None):
        files = FileBucketFiles.objects.filter(bucket=fileBucket).all()
        for file in files:
            file.delete()

    return True

@app.task
def UpdateCompanyNames():
    log.info('Updating company Names')
    admin_views.UpdateCompanyNamesTask()

    return