from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.conf import settings

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
    print("a")
    result = ExtractPages(document, start, end, False)
    print("here10")
    if result.code == "00000":
        # Extract Text from images
        pass
        #result = getDocumentText(document)

    # Cleanup Temporary Files
    if settings.USE_S3:
        tempFolder = document.file.file_location
        #fileModule.deleteDirectory(tempFolder,False)

    log.debug(f"Extraction complete. Result: {result.description} ({result.code})")
    return result

def RunPageTextAutomationView(request, did, data_type):
    result = RunPageTextAutomation(did, data_type)

    return redirect('document', did)

def RunPageTextAutomation(did, data_type):
    document = Document.objects.get(id=did)

    methods = ExtractionMethod.objects.filter(data_type=data_type)

    for method in methods:
        result = ExtractData(document,method)

    return True

