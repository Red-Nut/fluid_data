from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse

# Third party imports.
import json

from .data_extraction_functions import ExtractPages, getDocumentText, ExtractData

from data_extraction.models import *

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
    
    result = ExtractTextFromDocument(did, 1, 10)

    # Convert to Json and return the response.
    #return JsonResponse(result.description, safe=False)
    return redirect('document', did)

def ExtractTextFromDocument(did, start, end):
    document = Document.objects.get(id=did)

    # Convert file to images
    result = ExtractPages(document, start, end, False)
    if result.code == "00000":
        # Extract Text from images
        result = getDocumentText(document)
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

def MyFunction(request):
    wells = [
        "ARTHUR 107",
        "ARTHUR 108",
        "ARTHUR 218",
        "BLOODWORTH 155",
        "BORROWDALE 1",
        "BORROWDALE 119",
        "BORROWDALE 121",
        "BORROWDALE 122",
        "BORROWDALE 126",
        "BORROWDALE 153",
        "BORROWDALE 163",
        "BORROWDALE 166",
        "BORROWDALE 169",
        "BORROWDALE 172",
        "BORROWDALE 2",
        "BORROWDALE 232",
        "BORROWDALE 3",
        "BORROWDALE 4",
        "BORROWDALE 5",
        "BORROWDALE 6",
        "CAMERON 27",
        "CAMERON 28",
        "CAMERON 29",
        "CAMERON 31A",
        "CAMERON 31B",
        "CAMERON 32",
        "CAMERON 33",
        "CHARLIE 1",
        "CHARLIE 10",
        "CHARLIE 2",
        "CHARLIE 200",
        "CHARLIE 201",
        "CHARLIE 225",
        "CHARLIE 226",
        "CHARLIE 227",
        "CHARLIE 228",
        "CHARLIE 229",
        "CHARLIE 3",
        "CHARLIE 4",
        "CHARLIE 5",
        "CHARLIE 6",
        "CHARLIE 7",
        "CHARLIE 8",
        "CHARLIE 9",
        "DANIEL 1",
        "Fishburn 237",
        "Fishburn 238",
        "Fishburn 240",
        "FISHBURN 3",
        "FISHBURN 7",
        "GOLDEN GROVE 1",
        "GOLDEN GROVE 2",
        "GOLDEN GROVE 136",
        "GOLDEN GROVE 137",
        "GOLDEN GROVE 138",
        "GOLDEN GROVE 139",
        "GOLDEN GROVE 172",
        "GOLDEN GROVE 173",
        "GOLDEN GROVE 212",
        "PENRHYN 1",
        "PENRHYN 2",
        "PENRHYN 4",
        "PENRHYN 6",
        "PENRHYN 7",
        "PENRHYN 8",
        "PENRHYN 9",
        "PENRHYN 103",
        "PENRHYN 106",
        "PENRHYN 248",
        "PENRHYN 249",
        "PHILLIP 101",
        "PORTSMOUTH 126",
        "THACKERY 1",
        "THACKERY 2",
        "THACKERY 3",
        "THACKERY 4",
        "THACKERY 5",
        "THACKERY 6",
        "THACKERY 7",
        "THACKERY 231",
        "THACKERY 234",
        "THACKERY 235",
        "THACKERY 241",
        "THACKERY 242",
    ]

    results = []

    dataExtractionTypes = ExtractedDataTypes.objects.all()

    for well_name in wells:
        well = Well.objects.filter(well_name=well_name).first()
        for document in well.documents.all():
            if document.document_name.lower() == "well completion report":
                print(f"Extracting data from {well.well_name} - Well Completion Report")
                ExtractTextFromDocument(request, document.id)

                for type in dataExtractionTypes:
                    RunPageTextAutomation(request, document.id, type.id)
                
                print("complete")
                print(" ")
                results.append(well.well_name)


    response = {
		'results' : results,
	}

    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)