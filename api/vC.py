# Django imports.

from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.utils.timezone import make_aware

# Third party imports.
from pickle import FALSE
import json
from dateutil.parser import *
import math

# This module imports.

# Other module imports.
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose

# Global Variables
site = "fluiddata.com.au"
apiURL = "/api"
apiVersion = "/vC"
baseLink = site + apiURL + apiVersion

# Create your views here.
def index(request):
    return HttpResponse("API is running")

def retrieveId(request, id=0):
    # link
    link = baseLink + "/well/" + str(id) + "/"

    # Pagination Details

    pagination = {
        'supported' : False,
        'limit': 0,
        'start': 0,
        'end' : 0,
        'currentResultCount' : 1,
        'currentPage' : link,
        'nextPage' : "",
    },

    # No id specified.
    if(id==0):
        errorDes = "No well id specified."
        response = {
            'success': False,
            'errors':[
                errorDes
            ],
            'pagination' : pagination,
            'results':[],
        }
    else:
        # Get well data.
        well = Well.objects.filter(id=id).first()
        
        # No well found for supplied id.
        if(well is None):
            errorDes = "No well found with id: " + str(id) + "."
            response = {
                'success': False,
                'errors':[
                    errorDes
                ],
                'pagination' : pagination,
                'results':[],
            }
        
        # Success
        else:
            # Convert well to JSON data. 
            wellObject = WellJson(well)

            response = {
                'success': True,
                'errors':[],
                'pagination' : pagination,
                'results': [
                        wellObject
                ]
            }

    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)

def retrieveName(request, name="None"):
    # link
    link = baseLink + "/well/" + name + "/"

    # Pagination Details
    pagination = {
        'supported' : False,
        'limit': 0,
        'start': 0,
        'end' : 0,
        'currentResultCount' : 1,
        'currentPage' : link,
        'nextPage' : "",
    },

    # No name spcifed.
    if(name=="None"):
        errorDes = "No well name specified."
        response = {
            'success': False,
            'errors':[
                errorDes
            ],
            'pagination' : pagination,
            'results':[],
        }

    else:
        # Get well data.
        well = Well.objects.filter(well_name=name).first()
        
        # No well found for specified name.
        if(well is None):
            errorDes = "No well found with name: " + name
            response = {
                'success': False,
                'errors':[
                    errorDes
                ],
                'pagination' : pagination,
                'results':[],
            }

        # Success
        else:
            # Convert well to JSON data. 
            wellObject = WellJson(well)

            response = {
                'success': True,
                'errors':[],
                'pagination' : pagination,
                'results': [
                        wellObject
                ]
            }

    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)

def wellList(request):
    # Default limit:
    defaultLimit = 1000

    # link
    link = baseLink + "/wellList/"

    if request.method == 'GET':
        errors = []

        # Set result limit
        if 'limit' in request.GET:
            limitStr= request.GET['limit']
            try: 
                limit = int(limitStr)
            except:
                errors.append("Failed to convert provided limit variable to integer. limit = " + limitStr + ".")
                limit = defaultLimit
        else:
            limit = defaultLimit

        if 'start' in request.GET:
            startStr= request.GET['start']
            try: 
                start = int(startStr)
            except:
                errors.append("Failed to convert provided start variable to integer. start = " + startStr + ".")
                start = 0
        else:
            start = 0

        end = start + limit

        # Get well data.
        wells = Well.objects.all().order_by('well_name')

        # Limit results.
        if(start != None and start != '' and end != None and end != ''):
            wells = wells[start:end]

        # Create the list
        wellList = []
        currentCount = 0
        for well in wells:
            wellList.append(str(well))
            currentCount = currentCount + 1

        # Create link.
        currentLink = link + "?limit=" + str(limit) + "&start=" + str(start) 

        if currentCount == limit:
            nextLink = link + "?limit=" + str(limit) + "&start=" + str(end) 
        else: 
            nextLink= ""

        # Pagination Details
        end = end - 1
        pagination = {
            'supported' : True,
            'limit': limit,
            'start': start,
            'end' : end,
            'currentResultCount' : currentCount,
            'currentPage' : currentLink,
            'nextPage' : nextLink,
        },

        # Create the response object.
        response = {
            'success': True,
            'errors':errors,
            'pagination': pagination,
            'results': wellList,
        }

    else: 
        # Create the response object.
        errorDes = "Request method not supported: " + request.method + ". For this version of the API use GET."
        response = {
            'success': False,
            'errors':[
                errorDes
            ],
            'pagination': "",
            'results': [],
        }
        
    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)

def wellListID(request):
    # Default limit:
    defaultLimit = 1000

    # link
    link = baseLink + "/wellListID/"

    if request.method == 'GET':
        errors = []

        # Set result limit
        if 'limit' in request.GET:
            limitStr= request.GET['limit']
            try: 
                limit = int(limitStr)
            except:
                errors.append("Failed to convert provided limit variable to integer. limit = " + limitStr + ".")
                limit = defaultLimit
        else:
            limit = defaultLimit

        if 'start' in request.GET:
            startStr= request.GET['start']
            try: 
                start = int(startStr)
            except:
                errors.append("Failed to convert provided start variable to integer. start = " + startStr + ".")
                start = 0
        else:
            start = 0

        end = start + limit

        # Get well data     .
        wells = Well.objects.all()

        # Limit results.
        if(start != None and start != '' and end != None and end != ''):
            wells = wells[start:end]

        # Create the list
        wellList = []
        currentCount = 0
        for well in wells:
            wellObject = {
                'id' : well.id,
                'well_name' : well.well_name
            }

            wellList.append(wellObject)
            currentCount = currentCount + 1

        # Create link.
        currentLink = link + "?limit=" + str(limit) + "&start=" + str(start) 

        if currentCount == limit:
            nextLink = link + "?limit=" + str(limit) + "&start=" + str(end)
        else: 
            nextLink= "" 

        # Pagination Details
        end = end - 1
        pagination = {
            'supported' : True,
            'limit': limit,
            'start': start,
            'end' : end,
            'currentResultCount' : currentCount,
            'currentPage' : currentLink,
            'nextPage' : nextLink,
        },

        # Create the response object.
        response = {
            'success': True,
            'errors':[],
            'pagination': pagination,
            'results': wellList,
        }


    else: 
        # Create the response object.
        errorDes = "Request method not supported: " + request.method + ". For this version of the API use GET."
        response = {
            'success': False,
            'errors':[
                errorDes
            ],
            'pagination': "",
            'results': [],
        }
        
    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)

def search(request):
    # Default limit:
    defaultLimit = 1000

    # link
    link = baseLink + "/wellSearch/"

    if request.method == 'GET':
        errors = []

        # Set result limit
        if 'limit' in request.GET:
            limitStr= request.GET['limit']
            try: 
                limit = int(limitStr)
            except:
                errors.append("Failed to convert provided limit variable to integer. limit = " + limitStr + ".")
                limit = defaultLimit
        else:
            limit = defaultLimit

        if 'start' in request.GET:
            startStr= request.GET['start']
            try: 
                start = int(startStr)
            except:
                errors.append("Failed to convert provided start variable to integer. start = " + startStr + ".")
                start = 0
        else:
            start = 0

        end = start + limit
        
        currentLink = link + "?limit=" + str(limit) + "&start=" + str(start)
        nextLink = link + "?limit=" + str(limit) + "&start=" + str(end)

        # Initialise Query
        wellsQuery = Well.objects.all().order_by('well_name')

        # Filter: Name.
        if 'name' in request.GET:
            name= request.GET['name']
            searchTerms = name.split(' ')
            for searchTerm in searchTerms:
                wellsQuery = wellsQuery.filter(well_name__icontains=searchTerm)
            
            currentLink =  currentLink + "&name=" + name
            nextLink =  nextLink + "&name=" + name

        # Filter: Owner.
        if 'operator' in request.GET:
            owner= request.GET['operator']
            wellsQuery = wellsQuery.filter(owner__company_name__icontains=owner)

            currentLink =  currentLink + "&operator=" + owner
            nextLink =  nextLink + "&operator=" + owner

        # Filter: state.
        if 'state' in request.GET:
            state= request.GET['state']
            wellsQuery = wellsQuery.filter(state__name_long__icontains=state)

            currentLink =  currentLink + "&state=" + state
            nextLink =  nextLink + "&state=" + state

        # Filter: permit.
        if 'permit' in request.GET:
            permit= request.GET['permit']
            wellsQuery = wellsQuery.filter(permit__permit_number__icontains=permit)

            currentLink =  currentLink + "&permit=" + permit
            nextLink =  nextLink + "&permit=" + permit

        # Filter: Status.
        #if 'state' in request.GET:
        #    status= request.GET['state']
        #    wellsQuery = wellsQuery.filter(status__status_name__icontains=status)

        # Filter: Class.
        if 'class' in request.GET:
            wellClass= request.GET['class']
            wellsQuery = wellsQuery.filter(well_class__class_name__icontains=wellClass)

            currentLink =  currentLink + "&class=" + wellClass
            nextLink =  nextLink + "&class=" + wellClass

        # Filter: Purpose.
        if 'purpose' in request.GET:
            purpose= request.GET['purpose']
            wellsQuery = wellsQuery.filter(purpose__purpose_name__icontains=purpose)

            currentLink =  currentLink + "&purpose=" + purpose
            nextLink =  nextLink + "&purpose=" + purpose

        # Filter: Latitude.
        if 'lat_min' in request.GET:
            lat_min= request.GET['lat_min']
            wellsQuery = wellsQuery.filter(latitude__gte=lat_min)

            currentLink =  currentLink + "&lat_min=" + lat_min
            nextLink =  nextLink + "&lat_min=" + lat_min

        if 'lat_max' in request.GET:
            lat_max= request.GET['lat_max']
            wellsQuery = wellsQuery.filter(latitude__lte=lat_max)

            currentLink =  currentLink + "&lat_max=" + lat_max
            nextLink =  nextLink + "&lat_max=" + lat_max

        # Filter: Longitude.
        if 'long_min' in request.GET:
            long_min= request.GET['long_min']
            wellsQuery = wellsQuery.filter(longitude__gte=long_min)

            currentLink =  currentLink + "&long_min=" + long_min
            nextLink =  nextLink + "&long_min=" + long_min

        if 'long_max' in request.GET:
            long_max= request.GET['long_max']
            wellsQuery = wellsQuery.filter(longitude__lte=long_max)
            
            currentLink =  currentLink + "&long_max=" + long_max
            nextLink =  nextLink + "&long_max=" + long_max

        # Filter: Rig Release Date.
        if 'rig_release_start' in request.GET:
            rig_release_start= request.GET['rig_release_start']
            start = parse(rig_release_start)
            wellsQuery = wellsQuery.filter(rig_release__gte=start)

            currentLink =  currentLink + "&rig_release_start=" + rig_release_start
            nextLink =  nextLink + "&rig_release_start=" + rig_release_start

        if 'rig_release_end' in request.GET:
            rig_release_end= request.GET['rig_release_end']
            end = parse(rig_release_end)
            wellsQuery = wellsQuery.filter(rig_release__lte=end)

            currentLink =  currentLink + "&rig_release_end=" + rig_release_end
            nextLink =  nextLink + "&rig_release_end=" + rig_release_end

        # Filter: Modified Date.
        if 'modified_start' in request.GET:
            modified_start= request.GET['modified_start']
            start = make_aware(parse(modified_start)) # Make aware converts the date to datetime with timezone compatibility
            wellsQuery = wellsQuery.filter(date_modified__gte=start)

            currentLink =  currentLink + "&modified_start=" + modified_start
            nextLink =  nextLink + "&modified_start=" + modified_start

        if 'modified_end' in request.GET:
            modified_end= request.GET['modified_end']
            end = make_aware(parse(modified_end)) # Make aware converts the date to datetime with timezone compatibility
            wellsQuery = wellsQuery.filter(date_modified__lte=end)

            currentLink =  currentLink + "&modified_end=" + modified_end
            nextLink =  nextLink + "&modified_end=" + modified_end

        # Filter: Created Date.
        if 'created_start' in request.GET:
            created_start= request.GET['created_start']
            start = make_aware(parse(created_start))
            wellsQuery = wellsQuery.filter(date_created=start)

            currentLink =  currentLink + "&created_start=" + created_start
            nextLink =  nextLink + "&created_start=" + created_start

        if 'created_end' in request.GET:
            created_end= request.GET['created_end']
            end = make_aware(parse(created_end))
            wellsQuery = wellsQuery.filter(date_created=end)

            currentLink =  currentLink + "&created_end=" + created_end
            nextLink =  nextLink + "&created_end=" + created_end

        # Limit results.
        if(start != None and start != '' and end != None and end != ''):
            wellsQuery = wellsQuery[start:end]

        # Get well data.
        wells = []
        currentCount = 0
        for well in wellsQuery:
            wellObject = WellJson(well)
            wells.append(wellObject)

            currentCount = currentCount + 1

        # Next Page
        if currentCount == limit:
            nextLink = nextLink 
        else: 
            nextLink= ""

        # Pagination Details
        end = end - 1
        pagination = {
            'supported' : True,
            'limit': limit,
            'start': start,
            'end' : end,
            'currentResultCount' : currentCount,
            'currentPage' : currentLink,
            'nextPage' : nextLink,
        },

        # Create the response object.
        response = {
            'success': True,
            'errors':[],
            'pagination': pagination,
            'wells': wells,
        }
    else:
        # Create the response object.
        errorDes = "Request method not supported: " + request.method + ". For this version of the API use GET."
        response = {
            'success': False,
            'errors':[
                errorDes
            ],
            'pagination': "",
            'wellList': "",
        }

    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)


def WellJson(well):
    # Documents (not in report).
    documentObjects = Document.objects.filter(well=well, report__isnull=True).all()
    files = []
    for file in documentObjects:
        myFile = {
            'document_name' : file.document_name,
            #'file_name' : file.file.file_name + '.' + file.file.file_ext,
            'url' : file.url,
        }
        files.append(myFile)

    # Reports.
    reportObjects = Report.objects.filter(well=well).all()
    reports = []
    for report in reportObjects:
        documentObjects = Document.objects.filter(well=well, report=report).all()
        reportFiles = []
        for file in documentObjects:
            myFile = {
                'document_name' : file.document_name,
                #'file_name' : file.file.file_name + '.' + file.file.file_ext,
                'url' : file.url,
            }
            reportFiles.append(myFile)

        myReport = {
            'report_type' : str(report.report_type),
            'report_name' : report.report_name,
            'gov_name' : report.gov_report_name,
            'url' : report.url,
            'files' : reportFiles
        }
        reports.append(myReport)

    wellJson = {
        'id' : well.id,
        'well_name' : well.well_name,
        'gov_id' : well.gov_id,
        'operator' : str(well.owner),
        'state' : well.state.name_long,
        'permit' : str(well.permit),
        'status' : str(well.status),
        'class' : str(well.well_class),
        'purpose' : str(well.purpose),
        'latitude' : str(well.latitude),
        'longitude' : str(well.longitude),
        'rig_release_date' : str(well.rig_release),
        'url' : "https://geoscience.data.qld.gov.au/borehole/" + well.gov_id,
        'files' : files,
        'reports' : reports
    }

    return wellJson