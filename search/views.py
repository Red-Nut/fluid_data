from django.http import JsonResponse
from django.shortcuts import render
import json

from .APIsearch import APISearchQLD, WebScrapeSearchQLD, RetriveQLD, ResultEncoder


# Create your views here.
def SearchGov(request):
    #jsonStr = request.GET['data']
    #data = json.loads(jsonStr)
    data = json.loads(request.body.decode("utf-8"))

    searchStr=data['searchStr']
    method = data['method']
    attachmentsOnlyStr = data['attachmentsOnly']
    WCRonlyStr = data['WCRonly']
    includeExistingStr = data['includeExisting']
    #includeExistingStr = "Y"

    if(attachmentsOnlyStr == "Y"):
        attachmentsOnly = True
    else: 
        attachmentsOnly = False

    if(WCRonlyStr == "Y"):
        WCRonly = True
    else: 
        WCRonly = False

    if(includeExistingStr == "Y"):
        includeExisting = True
    else: 
        includeExisting = False

    if(method == "Web"):
        mySearch = WebScrapeSearchQLD(searchStr, attachmentsOnly, WCRonly, includeExisting)
    else:
        mySearch = APISearchQLD(searchStr,attachmentsOnly, WCRonly, includeExisting)

    mySearch.search()

    response = {'searchName':repr(mySearch),'results':ResultEncoder().encode(mySearch)}

    return JsonResponse(response)  # serialize and use JSON headers

def AddDatabase(request):
    #jsonStr = request.GET['data']
    #data = json.loads(jsonStr)
    data = json.loads(request.body.decode("utf-8"))

    wellId = data['id']
    state = data['state']

    response = Add(wellId,state)

    return JsonResponse(response)

def AddMany(request):
    #jsonStr = request.GET['data']
    #data = json.loads(jsonStr)
    data = json.loads(request.body.decode("utf-8"))

    wellList = data['wellList']

    responseList = []

    for well in wellList:
        response = Add(well['id'],well['state'] )
        responseList.append(response)

    response = {'results':ResultEncoder().encode(responseList)}

    return JsonResponse(response)
    

def Add(wellId,state):
    if state == "QLD":
        myRetrive = RetriveQLD(wellId)
        myRetrive.retrive()

    response = {'success':myRetrive.success,'wellName':myRetrive.wellName,'errors':ResultEncoder().encode(myRetrive.errors)}
    return response
