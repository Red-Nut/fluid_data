# Django imports.
from django.shortcuts import render, HttpResponse


# Third party imports.
import json
from dateutil.parser import *

# This module imports.

# Other module imports.
from data_extraction.functions import GetDocumentExt, GetDocumentLink
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose


# Create your views here.
def retrieveId(id):
    well = Well.objects.filter(id=id).first()
    
    if(well is None):
        return None
    else:
        wellObject = WellJson(well)

        return wellObject

def wellListID(orderBy):
    wells = Well.objects.all()

    if(orderBy is not None):
        wells = wells.order_by(orderBy)

    wellList = []
    for well in wells:
        wellObject = {
            'id' : well.id,
            'well_name' : well.well_name
        }

        wellList.append(wellObject)

    json_resonse = json.dumps(wellList)
    return json_resonse

def Search(name, owner, state, permit, status, wellClass, purpose, 
        lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
        orderBy):
    wellsQuery = Well.objects.all().order_by('well_name')

    # Filter: Name.
    if (name != None and name != ''):
        searchTerms = name.split(' ')
        for searchTerm in searchTerms:
            wellsQuery = wellsQuery.filter(well_name__icontains=searchTerm)

    # Filter: Owner.
    if (owner != None and owner != ''):
        wellsQuery = wellsQuery.filter(owner__company_name__icontains=owner)

    # Filter: state.
    if (state != None and state != ''):
        wellsQuery = wellsQuery.filter(state__name_long__icontains=state)

    # Filter: permit.
    if (permit != None and permit != ''):
        wellsQuery = wellsQuery.filter(permit__permit_number__icontains=permit)

    # Filter: Status.
    if (status != None and status != ''):
        wellsQuery = wellsQuery.filter(status__status_name__icontains=status)

    # Filter: Class.
    if (wellClass != None and wellClass != ''):
        wellsQuery = wellsQuery.filter(well_class__class_name__icontains=wellClass)

    # Filter: Purpose.
    if (purpose != None and purpose != ''):
        wellsQuery = wellsQuery.filter(purpose__purpose_name__icontains=purpose)

    # Filter: Latitude.
    if (lat_min != None and lat_min != ''):
        wellsQuery = wellsQuery.filter(latitude__gte=lat_min)

    if (lat_max != None and lat_max != ''):
        wellsQuery = wellsQuery.filter(latitude__lte=lat_max)

    # Filter: Longitude.
    if (long_min != None and long_min != ''):
        wellsQuery = wellsQuery.filter(longitude__gte=long_min)

    if (long_max != None and long_max != ''):
        wellsQuery = wellsQuery.filter(longitude__lte=long_max)

    # Filter: Rig Release Data.
    if (rig_release_start != None and rig_release_start != ''):
        #start = parse(rig_release_start)
        wellsQuery = wellsQuery.filter(rig_release__gte=rig_release_start)

    if (rig_release_end != None and rig_release_end != ''):
        #end = parse(rig_release_end)
        wellsQuery = wellsQuery.filter(rig_release__lte=rig_release_end)


    # Order results.
    if (orderBy == None or orderBy == ''):
        wellsQuery = wellsQuery.order_by('id')
    else:
        wellsQuery = wellsQuery.order_by(orderBy)

    return wellsQuery

def WellSearch(name, owner, state, permit, status, wellClass, purpose, 
        lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
        orderBy, start, end):

    wellsQuery = Search(name, owner, state, permit, status, wellClass, purpose, 
        lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
        orderBy)

    # Limit results.
    if(start != None and start != '' and end != None and end != ''):
        wellsQuery = wellsQuery[start:end]

    # Get well data.
    wells = []
    for well in wellsQuery:
        wellObject = WellJson(well)
        wells.append(wellObject)

    # Response
    response = {
        'wells' : wells
    }

    return response

def LASsearch(name, owner, state, permit, status, wellClass, purpose, 
        lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
        orderBy, start, end):


    wellsQuery = Search(name, owner, state, permit, status, wellClass, purpose, 
        lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
        orderBy)

 
    # Get well data.
    wells = []
    i = 1
    for well in wellsQuery:
        # Limit results.
        if end is not None:
            if i > end:
                break

        wellObject = WellJson(well)

        # Get LAS Files
        LASFiles = []
        lasCount = 0
        for document in wellObject['documents']:
            if document['ext'] == ".las":
                LASFiles.append(document)
                lasCount += 1

        wellObject['LASFiles'] = LASFiles
        wellObject['lasCount'] = lasCount

        
        # Filter LAS Files
        if lasCount > 0:
            i = i + 1
            # Limit results.
            if start is None or i >= start:
                wells.append(wellObject)


    # Response
    response = {
        'wells' : wells
    }

    return response

def WellJson(well):
    # Documents (not in report).
    documentObjects = Document.objects.filter(well=well, report__isnull=True).all()

    documents = []
    documentCount = 0
    for document in documentObjects:
        documentCount += 1
        ext = GetDocumentExt(document)
        link = GetDocumentLink(document)

        myDocument = {
            'id' : document.id,
            'document_name' : document.document_name,
            'ext' : ext,
            'status' :dict(Document.STATUS)[document.status],
            'link' : link,
            'gov_url' : document.url,
        }
        documents.append(myDocument)

    # Reports.
    reportObjects = Report.objects.filter(well=well).all()
    reports = []
    reportCount = 0
    for report in reportObjects:
        reportCount += 1
        documentObjects = Document.objects.filter(well=well, report=report).all()
        documentObjects = documentObjects.exclude(document_name__icontains="Report Geometry")
        documentObjects = documentObjects.exclude(document_name__icontains="OCR extract of report")

        reportDocuments = []
        reportDocumentsCount = 0
        for document in documentObjects:
            reportDocumentsCount += 1
            ext = GetDocumentExt(document)
            link = GetDocumentLink(document)
            
            myDocument = {
                'id' : document.id,
                'document_name' : document.document_name,
                'ext' : ext,
                'status' : dict(Document.STATUS)[document.status],
                'link' : link,
                'gov_url' : document.url,
            }
            reportDocuments.append(myDocument)

        myReport = {
            'id' : report.id,
            'report_type' : str(report.report_type),
            'report_name' : report.report_name,
            'gov_name' : report.gov_report_name,
            'url' : report.url,
            'documents' : reportDocuments,
            'document_count' : reportDocumentsCount
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
        'rig_release_date' : well.rig_release,
        'modified' : str(well.modified),
        'date_modified' : str(well.date_modified),
        'date_created' : str(well.date_created),
        'url' : well.url,
        'documents' : documents,
        'document_count' : documentCount,
        'reports' : reports,
        'report_count' : reportCount
    }

    return wellJson

def WellCount():
    return Well.objects.count()

def DocumentCount():
    return Document.objects.count()

def DocumentMissingCount():
    return Document.objects.filter(status=Document.MISSING).count()

def DocumentDownloadCount():
    return Document.objects.filter(status=Document.DOWNLOADED).count()

def DocumentIgnoredCount():
    return Document.objects.filter(status=Document.IGNORED).count()

def DocumentNotConvertedCount():
    return Document.objects.filter(conversion_status=Document.NOTCONVERTED).count()

def DocumentConvertedCount():
    return Document.objects.filter(conversion_status=Document.CONVERTED).count()

def DocumentIgnoreConvertedCount():
    return Document.objects.filter(conversion_status=Document.IGNORED).count()