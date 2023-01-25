from django.shortcuts import render, redirect
from django.http import JsonResponse

from .data_extraction_functions import ExtractPages, getDocumentText, ExtractData

from data_extraction.models import *

def ExtractTextFromDocument(request, did):
    document = Document.objects.get(id=did)

    # Convert file to images
    result = ExtractPages(document, 1,6, True)
    if result.code == "00000":
        # Extract Text from images
        result = getDocumentText(document)
    

    # Convert to Json and return the response.
    #return JsonResponse(result.description, safe=False)
    return redirect('document', did)

def RunPageTextAutomation(request, did, dataType):
    document = Document.objects.get(id=did)

    methods = ExtractionMethod.objects.filter(dataType=dataType)
    for method in methods:
        result = ExtractData(document,method)

    return redirect('document', did)