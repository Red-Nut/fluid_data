# Django imports
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q

# This module imports.
from .data_extraction_functions import ExtractPages, getDocumentText, ExtractData
from .isotherm_output import CreateIsothermTemplate

# Other module imports
from data_extraction.models import *
from file_manager import fileModule

# Third party imports.
import json





# Logging
import logging
log = logging.getLogger("interpretation")

def DataExtractionList(request):
    methods = ExtractionMethod.objects.order_by("name").all()

    context = {
        'methods' : methods,
    }


    return render(request, "data/data_extraction_list.html", context)


def DataExtractionView(request, id):

    method = ExtractionMethod.objects.get(id=id)

    context = {
        'method' : method,
    }


    return render(request, "data/data_extraction.html", context)

def ExtractTextFromDocumentView(request, did):
    result = ExtractTextFromDocument(did, 1, 99)

    # Convert to Json and return the response.
    #return JsonResponse(result.description, safe=False)
    return redirect('document', did)

def ExtractTextFromDocument(did, start, end):
    document = Document.objects.get(id=did)
    log.debug(f"Extracting Text from document: {document.document_name} ({document.id})")

    # Convert file to images
    result = ExtractPages(document, start, end, False)
    if result.code == "00000":
        # Extract Text from images
        result = getDocumentText(document)

    # Cleanup Temporary Files
    if settings.USE_S3:
        tempFolder = document.file.file_location
        fileModule.deleteDirectory(tempFolder,False)

    log.debug(f"Extraction complete. Result: {result.description} ({result.code})")
    return result

def RunPageTextAutomationView(request, did, data_type):
    result = RunPageTextAutomation(did, data_type)

    return redirect('document', did)

def RunPageTextAutomation(did, data_type):
    document = Document.objects.get(id=did)

    if document.conversion_status == document.IGNORED:
        return True

    if document.conversion_status == document.NOTCONVERTED:
        log.warning("Document not converted or only partially converted")

    if data_type == 0:
        methods = ExtractionMethod.objects.filter(
            Q(company__isnull=True) | Q(company=document.well.owner) | Q (company=document.report.report_owner)
        )
    else:
        methods = ExtractionMethod.objects.filter(data_type=data_type)
        methods = methods.filter(
            Q(company__isnull=True) | Q(company=document.well.owner) | Q (company=document.report.report_owner)
        )

    # exclude disabled methods
    methods = methods.exclude(enabled=False).all()

    for method in methods:
        print(f"Method: {method.name} ({method.id})")
        result = ExtractData(document,method)
        if result == False:
            log.warning('Text Extraction Failed. Document: %s (%i), Method: %s (%i)', document.document_name, document.id, method.name, method.id)

    return redirect('document', did)

def RunPageTextAutomationByMethodView(request, did, method_id):
    result = RunPageTextAutomationByMethod(did, method_id)

    return redirect('document', did)

def RunPageTextAutomationByMethod(did, method_id):
    document = Document.objects.get(id=did)
    method = ExtractionMethod.objects.get(id=method_id)

    #if document.conversion_status == document.IGNORED:
    #    return True

    result = ExtractData(document,method)
    if result == False:
        log.warning('Text Extraction Failed. Document: %s (%i), Method: %s (%i)', document.document_name, document.id, method.name, method.id)

    return redirect('document', did)

def CreateIsothermTemplateView(request, well_id):
    result = CreateIsothermTemplate(well_id)
    if result['success']:
        try:
            #Upload file to AWS
            well = Well.objects.get(id=well_id)
            folder = 'well_data/' + well.well_name + '/'
            fileModule.makeDirectory(folder, True)
            folder = folder + 'isotherms/'
            fileModule.makeDirectory(folder, True)
            destination = f"{folder}{result['fileName']}{result['fileExt']}"
            print(f"Destination: {destination}")
            print(f"path: {result['filePath']}")
            newResult = fileModule.uploadFileS3(result['filePath'],destination)
            print(newResult)

            # Add file to database
            file = File.objects.create(
                file_name = result['fileName'],
                file_ext = result['fileExt'],
                file_location = folder,
                file_size = result['fileSize']
            )

            # Create Document object
            document = Document.objects.create(
                document_name = result['fileName'],
                well = well,
                report = None,
                file = file,
                url = None,
                gov_id = None,
                status = Document.DOWNLOADED,
                converted = None,
                conversion_status = Document.IGNORED
            )

        except Exception as e:
            print(e)
        
        

    return redirect('details', well_id)

def MyFun(request):
    #try:
    # Scotia 44
    # Isotherm
    document = Document.objects.get(id=118481)
    if document:
        result = ExtractPages(document, None, None, False)
        if result.code == "00000":
            # Extract Text from images
            result = getDocumentText(document)
    # WCR
    document = Document.objects.get(id=118470)
    if document:
        result = ExtractPages(document, None, None, False)
        if result.code == "00000":
            # Extract Text from images
            result = getDocumentText(document)
    #except:
    #    print("failed Scotia 44")


    try:
        # Peat 47
        # Isotherm
        document = Document.objects.get(id=164552)
        if document:
            result = ExtractPages(document, None, None, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document)
        # WCR
        document = Document.objects.get(id=180805)
        if document:
            result = ExtractPages(document, None, None, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document)
    except:
        print("failed Peat 47")

    if False:
        # Peat 45
        document = Document.objects.get(id=161938)
        if document:
            result = ExtractPages(document, 1, 7, False)
            result = ExtractPages(document, 705, 705, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document)

        # Peat 46
        document = Document.objects.get(id=161942)
        if document:
            result = ExtractPages(document, 1, 7, False)
            result = ExtractPages(document, 499, 499, False)
            result = ExtractPages(document, 507, 507, False)
            result = ExtractPages(document, 581, 581, False)
            result = ExtractPages(document, 586, 586, False)
            result = ExtractPages(document, 593, 593, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document)

        # Peat 47
        document = Document.objects.get(id=164540)
        if document:
            result = ExtractPages(document, 1, 6, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document)   

        # Peat 444
        document = Document.objects.get(id=180809)
        if document:
            result = ExtractPages(document, 1, 6, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document) 

        # Acrux 144
        document = Document.objects.get(id=158188)
        if document:
            result = ExtractPages(document, 1, 7, False)
            if result.code == "00000":
                # Extract Text from images
                result = getDocumentText(document) 

        try:
            # Acrux 145
            document = Document.objects.get(id=148761)
            if document:
                result = ExtractPages(document, 1, 8, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Acrux 145")

        try:
            # Acrux 146
            document = Document.objects.get(id=147747)
            if document:
                result = ExtractPages(document, 1, 7, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Acrux 146")

        try:
            # Polaris 140
            document = Document.objects.get(id=135737)
            if document:
                result = ExtractPages(document, 1, 9, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Polaris 140")

        try:
            # Polaris 142
            document = Document.objects.get(id=135629)
            if document:
                result = ExtractPages(document, 1, 8, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Polaris 142")

        try:
            # Polaris 150
            document = Document.objects.get(id=133081)
            if document:
                result = ExtractPages(document, 1, 8, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Polaris 150")

        try:
            # Scotia 34
            document = Document.objects.get(id=119136)
            if document:
                result = ExtractPages(document, 1, 13, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Scotia 34")

        try:
            # Scotia 35
            document = Document.objects.get(id=118470)
            if document:
                result = ExtractPages(document, 1, 13, False)
                if result.code == "00000":
                    # Extract Text from images
                    result = getDocumentText(document) 
        except:
            print("failed Scotia 35")

        try:
            # Scotia 44
            document = Document.objects.get(id=148936)
            if document:
                result = getDocumentText(document) 
        except:
            print("failed Scotia 44")

        try:
            # Scotia 45
            document = Document.objects.get(id=118470)
            if document:
                result = getDocumentText(document) 
        except:
            print("failed Scotia 45")

