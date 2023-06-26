# Django imports.
from django.http import JsonResponse
from django.shortcuts import HttpResponse

# Third party imports.
import json

# This module imports.
from .APIsearch import APISearchQLD, WebScrapeSearchQLD, Add, UpdateQLD, RetreiveAllQLD, SearchStrQLD, ResultEncoder

# Other module imports.
from data_extraction.models import *
from data_extraction.functions import ConvertToTrueFalse
from data_extraction.responseCodes import Result, GenerateResult, PrintResultLog, searchList as resultList
from data_extraction import tasks
from interpretation.views import ExtractTextFromDocument, RunPageTextAutomation
from file_manager import fileModule

# Logging
import logging
log = logging.getLogger("search")

def SearchGov(request):
    # Load request variables.
    data = json.loads(request.body.decode("utf-8"))

    searchStr=data['searchStr']
    method = data['method']
    attachmentsOnlyStr = data['attachmentsOnly']
    WCRonlyStr = data['WCRonly']
    includeExistingStr = data['includeExisting']

    # Convert Y/N to True/False.
    attachmentsOnly = ConvertToTrueFalse(attachmentsOnlyStr)
    WCRonly = ConvertToTrueFalse(WCRonlyStr)
    includeExisting = ConvertToTrueFalse(includeExistingStr)

    # Select the appropriate search method.
    if(method == "Web"):
        # Note web scrapping is not currently being developed as the API has now been rolled out.
        mySearch = WebScrapeSearchQLD(searchStr, attachmentsOnly, WCRonly, includeExisting)
    else:
        mySearch = APISearchQLD(searchStr,attachmentsOnly, WCRonly, includeExisting)

    # Run the search.
    mySearch.search()

    # Put the results into a reponse.
    response = {'searchName':repr(mySearch),'results':ResultEncoder().encode(mySearch)}

    # Convert to Json and return the response.
    return JsonResponse(response)

def AddDatabase(request, state, pid):
    package = Package.objects.filter(gov_id=pid).first()
    if package is None:
        check = False
        try:
            package = Package.objects.create(gov_id=pid)
            check=True
        except Exception as e:
            result = GenerateResult(resultList,36)
            PrintResultLog(result)
        
        if check:
            response = Add(package,state)
            return JsonResponse(response)
    else:
        response = Add(package,state)
        return JsonResponse(response)

    response = None
    return JsonResponse(response)
    

def ManualAdd(request,id):

    response = Add(id,"QLD")

    # Convert to Json and return the response.
    return JsonResponse(response)

def AddMany(request):
    data = json.loads(request.body.decode("utf-8"))

    wellList = data['wellList']

    responseList = []

    for well in wellList:
        response = Add(well['id'],well['state'] )
        responseList.append(response)

    response = {'results':ResultEncoder().encode(responseList)}

    return JsonResponse(response)
    
def UpdateAllQLD(request):
    responseList = RetreiveAllQLD()
    print(responseList)
    
    return JsonResponse(responseList, safe=False)

    #response = {'results':ResultEncoder().encode(responseList)}
    #return JsonResponse(response, safe=False)

def UpdateNewQLD(request):
    log.info("Running daily QLD update function.")

    responseList = UpdateQLD()
    log.debug(responseList)

    for response in responseList:
        if response['package'] != "Deleted":
            well = Well.objects.filter(well_name=response['well_name']).first()
            if well is not None:
                for document in well.documents.all():
                    if document.report is not None:
                        if document.report.report_type.type_name == "Well Completion Report":
                            log.debug(f"Document sent to celery for processing. Well: {well.well_name} ({well.id}), Document: {document.document_name} ({document.id})")
                            tasks.ProcessDocument.delay(document.id)
            else:
                log.warning(f"Well not processed as does not exist in the system. Well: {response['well_name']}")
    
    return JsonResponse(responseList, safe=False)

def MyFunction(request):
    log.debug("Running my function")

    wells = [
        "BURUNGA 2",
        "BURUNGA 2A",
        "BURUNGA LANE 4",
        "BURUNGA LANE 5",
        "BURUNGA LANE 6",
        "PEAT 1",
        "PEAT 10",
        "PEAT 15",
        "PEAT 16",
        "PEAT 444",
        "PEAT 45",
        "PEAT 46",
        "PEAT 47",
        "SCOTIA 34",
        "SCOTIA 35",
        "SCOTIA 44",
        "SCOTIA 45",
        "SOUTH BURUNGA 2",
        "POLARIS 140",
        "POLARIS 142",
        "POLARIS 150",
        "ACRUX 144",
        "ACRUX 145",
        "ACRUX 146",
    ]

    results = []

    for well_name in wells:
        well = Well.objects.filter(well_name=well_name).first()
        documents = well.documents.all()
        for document in documents:
            if document.status != document.DOWNLOADED:
                result = fileModule.downloadWellFile(document)
                if(result.code != "00000"):
                    # Failed, notify users
                    log.error(f"({document.id}) Document not downloaded. Document: {document.id}, Error {result.code}: {result.description}")
                    results.append(f"Error {result.code}: {result.description}")

    response = {
		'results' : results,
	}

    json_resonse = json.dumps(response)

    return HttpResponse(json_resonse)

    for well_name in wells:
        well = Well.objects.filter(well_name=well_name).first()
        if well is None:
            results.append(f"New Well Added: {well.well_name}")
            log.debug(f"New Well Added: {well.well_name}")
        else: 
            results.append(f"Processing Well: {well.well_name}")
            log.debug(f"Processing Well: {well.well_name}")
        searchResults = SearchStrQLD(well_name)
        for result in searchResults:
            if 'errors' in result:
                if 'success' in result:
                    if result['success'] == False:
                        result['errors'] = json.loads(result['errors'])
                        for error in result['errors']:
                            log.error(error)
            results.append(result)

        well = Well.objects.filter(well_name=well_name).first()
        for document in well.documents.all():
            if document.report is not None:
                if document.report.report_type.type_name == "Well Completion Report":
                    log.debug(f"Document sent to celery for processing. Well: {well_name} ({well.id}), Document: {document.document_name} ({document.id})")
                    tasks.ProcessDocument.delay(document.id)



    response = {
		'results' : results,
	}

    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)



