from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q

# Third party imports.
import json

from .data_extraction_functions import ExtractPages, getDocumentText, ExtractData

from data_extraction.models import *
from file_manager import fileModule

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
        return False

    if data_type == 0:
        methods = ExtractionMethod.objects.filter(
            Q(company__isnull=True) | Q(company=document.well.owner) | Q (company=document.report.report_owner)
        )
    else:
        methods = ExtractionMethod.objects.filter(data_type=data_type)
        methods = methods.filter(
            Q(company__isnull=True) | Q(company=document.well.owner) | Q (company=document.report.report_owner)
        )

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

    if document.conversion_status == document.IGNORED:
        return True

    if document.conversion_status == document.NOTCONVERTED:
        return False

    result = ExtractData(document,method)
    if result == False:
        log.warning('Text Extraction Failed. Document: %s (%i), Method: %s (%i)', document.document_name, document.id, method.name, method.id)

    return redirect('document', did)