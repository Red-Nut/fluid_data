# Django imports.
from django.shortcuts import render, HttpResponse
import datetime
from django.conf import settings
from django.utils.timezone import make_aware

# Third party imports.
import json
from dateutil.parser import *

# This module imports.

# Other module imports.
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose


# Create your views here.
def index(request):
    return HttpResponse("API is running")

def retrieveId(request, id=0):
    if(id==0):
        return HttpResponse("Specify a well id.")
    else:
        well = Well.objects.filter(id=id).first()
        
        if(well is None):
            return HttpResponse("No well found with id: " + str(id))
        else:
            wellObject = WellJson(well)

            # Response
            response = {
                'wells': [
                        wellObject
                ]
            }

            json_resonse = json.dumps(response)
            return HttpResponse(json_resonse)

def retrieveName(request, name="None"):
    if(name=="None"):
        return HttpResponse("Specify a well name.")
    else:
        well = Well.objects.filter(well_name=name).first()
        
        if(well is None):
            return HttpResponse("No well found with name: " + name)
        else:
            wellObject = WellJson(well)

            # Response
            response = {
                'wells': [
                        wellObject
                ]
            }

            json_resonse = json.dumps(response)
            return HttpResponse(json_resonse)

def wellList(request):
    wells = Well.objects.all().order_by('well_name')

    wellList = []
    for well in wells:
        wellList.append(str(well))

    json_resonse = json.dumps(wellList)
    return HttpResponse(json_resonse)

def wellListID(request):
    wells = Well.objects.all()

    wellList = []
    for well in wells:
        wellObject = {
            'id' : well.id,
            'well_name' : well.well_name
        }

        wellList.append(wellObject)

    json_resonse = json.dumps(wellList)
    return HttpResponse(json_resonse)

def search(request):
    if request.method == 'GET':
        wellsQuery = Well.objects.all().order_by('well_name')
        # Filter: Name.
        if 'name' in request.GET:
            name= request.GET['name']
            searchTerms = name.split(' ')
            for searchTerm in searchTerms:
                wellsQuery = wellsQuery.filter(well_name__icontains=searchTerm)

        # Filter: Owner.
        if 'operator' in request.GET:
            owner= request.GET['operator']
            wellsQuery = wellsQuery.filter(owner__company_name__icontains=owner)

        # Filter: state.
        if 'state' in request.GET:
            state= request.GET['state']
            wellsQuery = wellsQuery.filter(state__name_long__icontains=state)

        # Filter: permit.
        if 'permit' in request.GET:
            permit= request.GET['permit']
            wellsQuery = wellsQuery.filter(permit__permit_number__icontains=permit)

        # Filter: Status.
        #if 'state' in request.GET:
        #    status= request.GET['state']
        #    wellsQuery = wellsQuery.filter(status__status_name__icontains=status)

        # Filter: Class.
        if 'class' in request.GET:
            wellClass= request.GET['class']
            wellsQuery = wellsQuery.filter(well_class__class_name__icontains=wellClass)

        # Filter: Purpose.
        if 'purpose' in request.GET:
            purpose= request.GET['purpose']
            wellsQuery = wellsQuery.filter(purpose__purpose_name__icontains=purpose)

        # Filter: Latitude.
        if 'lat_min' in request.GET:
            lat_min= request.GET['lat_min']
            wellsQuery = wellsQuery.filter(latitude__gte=lat_min)

        if 'lat_max' in request.GET:
            lat_max= request.GET['lat_max']
            wellsQuery = wellsQuery.filter(latitude__lte=lat_max)

        # Filter: Longitude.
        if 'long_min' in request.GET:
            long_min= request.GET['long_min']
            wellsQuery = wellsQuery.filter(longitude__gte=long_min)

        if 'long_max' in request.GET:
            long_max= request.GET['long_max']
            wellsQuery = wellsQuery.filter(longitude__lte=long_max)

        # Filter: Rig Release Date.
        if 'rig_release_start' in request.GET:
            rig_release_start= request.GET['rig_release_start']
            start = parse(rig_release_start)
            wellsQuery = wellsQuery.filter(rig_release__gte=start)

        if 'rig_release_end' in request.GET:
            rig_release_end= request.GET['rig_release_end']
            end = parse(rig_release_end)
            wellsQuery = wellsQuery.filter(rig_release__lte=end)

        # Filter: Modified Date.
        if 'modified_start' in request.GET:
            modified_start= request.GET['modified_start']
            start = make_aware(parse(modified_start)) # Make aware converts the date to datetime with timezone compatibility
            wellsQuery = wellsQuery.filter(date_modified__gte=start)

        if 'modified_end' in request.GET:
            modified_end= request.GET['modified_end']
            end = make_aware(parse(modified_end)) # Make aware converts the date to datetime with timezone compatibility
            wellsQuery = wellsQuery.filter(date_modified__lte=end)

        # Filter: Created Date.
        if 'created_start' in request.GET:
            created_start= request.GET['created_start']
            start = make_aware(parse(created_start))
            wellsQuery = wellsQuery.filter(date_created=start)

        if 'created_end' in request.GET:
            created_end= request.GET['created_end']
            end = make_aware(parse(created_end))
            wellsQuery = wellsQuery.filter(date_created=end)

        # Get well data.
        wells = []
        for well in wellsQuery:
            wellObject = WellJson(well)
            wells.append(wellObject)

        # Response
        response = {
            'wells' : wells
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