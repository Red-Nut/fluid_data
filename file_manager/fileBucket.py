from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from background_task import background

from data_extraction.models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose, UserFileBucket, FileBucketFiles
from data_extraction.myExceptions import Error, downloadList as errorList
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
        if(result.code != "50000"):
            # Failed, notify users
            print("file not downloaded")
            print(result.code)
        else:
            try:
                file = File.objects.filter(
                    file_name = result.file_name,
                    file_ext = result.file_ext,
                    file_location = result.file_location
                ).first()
                if(file is None):
                    file = File.objects.create(
                        file_name = result.file_name,
                        file_ext = result.file_ext,
                        file_location = result.file_location,
                        file_size = result.file_size
                    )
                else:
                    result = errorList[5]
                    result.description = result.description
                    result.consolLog = result.consolLog
                    print(result.consolLog)

                document.file = file
                document.status = 2
                document.save()

            except Exception as e:
                result = errorList[3]
                result.description = result.description
                result.consolLog = result.consolLog
                print(result.consolLog)

    # Create File Bucket
    root_folder = settings.MEDIA_ROOT + 'file_buckets/'
    if (not os.path.isdir(root_folder)):
        try:
            os.mkdir(root_folder)
        except Exception as e:
            myError = errorList[1]
            error = Error(myError.code,myError.description,myError.consolLog)
            print(f"Error {error.code}: {error.consolLog}")

            return error
	
    destination = root_folder + userFileBucket.name + '/'
    if (not os.path.isdir(destination)):
        try:
            os.mkdir(destination)
        except Exception as e:
            myError = errorList[1]
            error = Error(myError.code,myError.description,myError.consolLog)
            print(f"Error {error.code}: {error.consolLog}")

            return error

    # Copy Files
    for document in documents:
        sPath = settings.MEDIA_ROOT + 'well_data/' + document.file.file_location + document.file.file_name + document.file.file_ext
        dPath = destination + document.well.well_name + '/' + document.file.file_name + document.file.file_ext

        if (not os.path.isdir(destination + document.well.well_name)):
            try:
                os.mkdir(destination + document.well.well_name)
            except Exception as e:
                myError = errorList[1]
                error = Error(myError.code,myError.description,myError.consolLog)
                print(f"Error {error.code}: {error.consolLog}")

                return error

        if(not os.path.exists(dPath)):
            try:
                shutil.copyfile(sPath,dPath)
            except Exception as e:
                myError = errorList[4]
                error = Error(myError.code,myError.description,myError.consolLog)
                error.description = error.description + ". Well: " + document.well.well_name + ". Document: " + document.document_name
                error.consolLog = error.consolLog + ". Well: " + document.well.well_name + ". Document: " + document.document_name
                print(f"Error {error.code}: {error.consolLog}")
                print(e)

                return error

    # Zip Folder
    zipName = root_folder + userFileBucket.name
    shutil.make_archive(zipName, 'zip', destination)

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