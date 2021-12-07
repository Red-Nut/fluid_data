# Django imports.
from django.http import JsonResponse

# Third party imports.
import json

# This module imports.
from .APIsearch import APISearchQLD, WebScrapeSearchQLD, Add, RetreiveAllQLD, ResultEncoder

# Other module imports.
from data_extraction.functions import ConvertToTrueFalse

# Create your views here.
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

def AddDatabase(request):
    # Load request variables.
    data = json.loads(request.body.decode("utf-8"))

    wellId = data['id']
    state = data['state']

    # Run the add well function. 
    response = Add(wellId,state)

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
    response = {'results':ResultEncoder().encode(responseList)}

    return JsonResponse(response)





