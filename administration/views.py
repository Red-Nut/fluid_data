# Django imports.
from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import Max, Count

# Third party imports.
import json
import time

# This module imports.

# Other module imports.
from data_extraction.functions import ResultEncoder, NumberToText, CleanStr, CleanURL, GetExtFromFileNameOrPath
from data_extraction.models import *
from data_extraction import myExceptions
from data_extraction import tasks
from search import config_search
from file_manager import fileModule, convertToJPEG
from interpretation import googleText
from api import internalAPI
from file_manager import fileModule

# Logging
import logging
log = logging.getLogger("administration")

def index(request):
    totalWells = internalAPI.WellCount()
    documentCount = internalAPI.DocumentCount()
    documentMissingCount = internalAPI.DocumentMissingCount()
    documentDownloadCount = internalAPI.DocumentDownloadCount()
    documentIgnoredCount = internalAPI.DocumentIgnoredCount()
    documentNotConvertedCount = internalAPI.DocumentNotConvertedCount()
    documentConvertedCount = internalAPI.DocumentConvertedCount()
    documentIgnoreConvertedCount = internalAPI.DocumentIgnoreConvertedCount()

    companies = Company.objects.order_by("company_name").all()

    context = {
        # Well Data
		"totalWells" :  totalWells,
        "totalWellsStr" :  NumberToText(totalWells),

        # Document Data
        "documentCount" :  documentCount,
        "documentCountStr" :  NumberToText(documentCount),

        # Document Download Data
        "documentMissingCount" :  documentMissingCount,
        "documentMissingCountStr" :  NumberToText(documentMissingCount),
        "documentDownloadCount" :  documentDownloadCount,
        "documentDownloadCountStr" :  NumberToText(documentDownloadCount),
        "documentIgnoredCount" :  documentIgnoredCount,
        "documentIgnoredCountStr" :  NumberToText(documentIgnoredCount),

        # Document Conversion Data
        "documentNotConvertedCount" :  documentNotConvertedCount,
        "documentNotConvertedCountStr" :  NumberToText(documentNotConvertedCount),
        "documentConvertedCount" :  documentConvertedCount,
        "documentConvertedCountStr" :  NumberToText(documentConvertedCount),
        "documentIgnoreConvertedCount" :  documentIgnoreConvertedCount,
        "documentIgnoreConvertedCountStr" :  NumberToText(documentIgnoreConvertedCount),

        # Company Data
        "companies" : companies,
        "companyCountStr" : NumberToText(companies.count()),
        
	}
    return render(request, "administration/index.html", context)

def Companies(request,id):
    company = Company.objects.filter(id=id).first()
    wells = Well.objects.filter(owner=company).all()

    context = {
		"company" :  company,
        "wells" :  wells,        
	}
    return render(request, "administration/company.html", context)

def UsersPage(request):
    userProfiles = UserProfile.objects.order_by("organisation").order_by("user__username").all()
    users = User.objects.order_by("username").all()

    
    for user in userProfiles:
        users = users.exclude(id=user.user.id)

    context = {
        "users" : users,
        "userProfiles" : userProfiles,
    }

    return render(request, "administration/users.html", context)

def WellsPage(request,page):
    totalWells = internalAPI.WellCount()
    wells = Well.objects.all()
    
    # Order results.
    wells = wells.order_by("well_name")

    # Limit results.
    start = page*100
    end = (page+1)*100
    if(start != None and start != '' and end != None and end != ''):
        wells = wells[start:end]

    context = {
        "totalWells" : totalWells,
        "wells" : wells,
        "page" : page,
    }

    return render(request, "administration/wells.html", context)

def WellsByLetter(request,letter,page):
    wells = Well.objects.filter(well_name__startswith=letter).all()
    
    # Order results.
    wells = wells.order_by("well_name")

    # Limit results.
    start = page*100
    end = (page+1)*100
    if(start != None and start != '' and end != None and end != ''):
        wells = wells[start:end]

    context = {
        "wells" : wells,
        "page" : page,
        "letter" : letter,
    }

    return render(request, "administration/wells.html", context)

def ConversionPage(request):
    WCRs = Report.objects.filter(report_type__type_name="Well Completion Report").all()

    WCRs_d = []
    WCRs_d_no = []
    WCRs_blank = []

    WCRs_c = []
    WCRs_c_no = []


    for WCR in WCRs:
        documents = Document.objects.filter(report=WCR).all()
        myWCR = {
            'id' : WCR.well.id,
            'report_name' : WCR.report_name
        }
        if(documents.count() == 0):
            WCRs_blank.append(myWCR)
        else:
            downloaded = True
            converted = False

            for document in documents:
                if document.status == 1: # missing
                    downloaded = False
                if document.converted == True:
                    converted = True

            if downloaded:
                WCRs_d.append(myWCR)
            else:
                WCRs_d_no.append(myWCR)

            if converted:
                WCRs_c.append(myWCR)
            else:
                WCRs_c_no.append(myWCR)


    # Array counts
    # Downloaded
    count_WCRs_d = len(WCRs_d)
    count_WCRs_d_no = len(WCRs_d_no)
    count_WCRs_blank = len(WCRs_blank)
    # Converted
    count_WCRs_c = len(WCRs_c)
    count_WCRs_c_no = len(WCRs_c_no)

    context = {
        'WCRs_d' : WCRs_d,
        'count_WCRs_d' : count_WCRs_d,
        'WCRs_d_no' : WCRs_d_no,
        'count_WCRs_d_no' : count_WCRs_d_no,
        'WCRs_blank' : WCRs_blank,
        'count_WCRs_blank' : count_WCRs_blank,
        'WCRs_c' : WCRs_c,
        'count_WCRs_c' : count_WCRs_c,
        'WCRs_c_no' : WCRs_c_no,
        'count_WCRs_c_no' : count_WCRs_c_no,
    }

    return render(request, "administration/index.html", context)

def ExtractionPage(request):
	return render(request, "administration/search.html")

def UpdateCompanyNames(request):
    tasks.UpdateCompanyNames.delay()

    return redirect(index)

def UpdateCompanyNamesTask():
    companies = Company.objects.all()
    #wells = Well.objects.filter(owner__company_name = "Tri-Star Australia Holding Company").all()

    for company in companies:
        correction = CompanyNameCorrections.objects.filter(alternateName=company.company_name).first()

        # Select or create the company object.
        if(correction is not None):
            # Filter not working as case sensitive
            if correction.alternateName == company.company_name:
                correctCompany = Company.objects.filter(company_name=correction.correctName).first()
                if (correctCompany is None):
                    try:
                        correctCompany = Company.objects.create(company_name = correction.correctName)
                    except:
                        # Handle Error
                        print("Failed to create new company.")
                        return
                
                # Assign company to each well.
                wells = Well.objects.filter(owner=company).all()
                for well in wells:
                    well.owner = correctCompany
                    well.save()
                    print("Updated " + company.company_name + " to " + correctCompany.company_name + " for " + well.well_name)

                # Check if old company can be deleted.
                check = Well.objects.filter(owner=company).first()

                if(check is None):
                    # Delete old company object
                    try:
                        company.delete()
                        print("Successfully deleted company: " + company.company_name)
                    except:
                        print("Failed to delete company: " + company.company_name)
    
    companies = Company.objects.all()
    for company in companies:
        # Check if old company can be deleted.
        check = Well.objects.filter(owner=company).first()

        if(check is None):
            # Delete old company object
            oldCompany = Company.objects.filter(company_name=company.company_name).first()
            owner = oldCompany.company_name
            try:
                oldCompany.delete()
                print("Successfully deleted company: " + owner)
            except:
                print("Failed to delete company: " + owner)

    return


def DownloadAllMissing(request):
	documents = Document.objects.filter(status=1).all()

	results=DownloadMissingFiles(documents)

	json_resonse = json.dumps(results)
	return HttpResponse(json_resonse)

def DownloadFilesForWell(request,id):
    well = Well.objects.filter(id=id).first()
    documents = Document.objects.filter(well=well).all()

    results=DownloadMissingFiles(documents)

    json_resonse = json.dumps(results)
    return HttpResponse(json_resonse)

def DeleteAllFiles(request):
    documents = Document.objects.all()

    for document in documents:
        document.status = 1
        document.save

    files = File.objects.all()
    for file in files:
        file.delete()

    return HttpResponse("done")

def DownloadAllWCRs(request):
    documents = Document.objects.filter(status=1).all()
    documents = documents.filter(report__report_type__type_name="Well Completion Report").all()
    documents = documents.filter(Q(url__icontains=".pdf")| Q(url__icontains='.tiff') | Q(url__icontains='.tif') | Q(url__icontains='.las') | Q(url__icontains='.json')).all()
    #print(documents.count())
    documents = documents.order_by("well__well_name")
	
    results=DownloadMissingFiles(documents)

    json_resonse = json.dumps(results)
    return HttpResponse(json_resonse)

def DownloadMissingFiles(documents):
    results=[]
    wellName = ""
    for document in documents:
        if(wellName != document.well.well_name):
            wellName = document.well.well_name
            print(" ")
            print(wellName.upper())
        print("    " + document.document_name)
        url = document.url

        if url is None :
            document.status = 3
            document.save()

            results.append("Ignored: " + document.document_name)

        elif ("report geometry" in document.document_name.lower() 
            or "ocr extract of report" in document.document_name.lower()
            or ".json" in document.document_name.lower()):
            document.status = 3
            document.save()

            results.append("Ignored: " + document.document_name)
        else: 
            #print("DOWNLOADING FILE - Well: " + document.well.well_name + " File: " + document.document_name)
            result = fileModule.downloadWellFile(document)
            if result.code == "50000":
                try:
                    file = File.objects.filter(
                        file_name = result.file_name,
                        file_ext = result.file_ext,
                        file_location = result.file_location
                    ).first()
                    if(file is None):
                        file = File.objects.create(
                            file_name = result.file_name,
                            file_ext = result.file_ext,
                            file_location = result.file_location,
                            file_size = result.file_size
                        )
                    else:
                        result = myExceptions.downloadList[5]
                        result.description = result.description
                        result.consolLog = result.consolLog
                        print(result.consolLog)

                    document.file = file
                    document.status = 2
                    document.save()

                except Exception as e:
                    result = myExceptions.downloadList[3]
                    result.description = result.description
                    result.consolLog = result.consolLog
                    print(result.consolLog)

            time.sleep(0.2)

            results.append(result.description)
        

    return results

def ConvertAllMissingToJPEG(request):
	documents = Document.objects.filter(converted=False).all()
	documents = documents.filter(status=2).all()
	documents = documents.filter(Q(file__file_ext='.pdf') | Q(file__file_ext='.tiff') | Q(file__file_ext='.tif')).all()

	print("Documents:" + str(documents.count()))

	results=[]

	for document in documents:
		result = convertToJPEG.convertFile(document)
		if result.code == "55000":
			result.success = True

			#update converted flag for document
			document.converted = True
			document.save()
		else:
			result.success = False

		results.append(result.description)

	json_resonse = json.dumps(results)
	return HttpResponse(json_resonse)

def ConvertToJPEG(request,id):
    document = Document.objects.filter(id=id).first()
    result = convertToJPEG.convertFile(document)
    
    response = ResultEncoder().encode(result)
    json_resonse = json.dumps(response)
    return HttpResponse(json_resonse)

def RemoveDuplicateDocuments(request):
	allDocs = Document.objects.all()

	count = 0

	for doc in allDocs:
		duplicates = Document.objects.filter(document_name=doc.document_name,well=doc.well,report=doc.report).exclude(id=doc.id).all()
		for dup in duplicates:
			print("Duplicate found. Well: " + str(dup.well) + " Document: " + dup.document_name)
			dup.delete()
			count = count + 1

	response = count

	return HttpResponse(str(response))

def changeWell(request):
    dWell = Well.objects.filter(well_name="259").first()
    nWell = Well.objects.filter(well_name="Bycoe 1").first()

    reports = Report.objects.filter(well=dWell).all()
    documents = Document.objects.filter(well=dWell).all()

    for report in reports:
        print("Report:" + report.report_name)
        report.well = nWell
        report.save()

    for document in documents:
        print("Document:" + document.document_name)
        document.well = nWell
        document.save()


    return HttpResponse("Done")

def GoogleText(request):
	documents = Document.objects.filter(converted=True).all()

	for document in documents:
		result = googleText.getDocumentText(document)

	return HttpResponse("done")

def myCreateUser(request):
    

    return HttpResponse("done")

def createUser(email, password, fname, lname):
    user = User.objects.create_user(email, email, password)
    user.first_name = fname
    user.last_name = lname
    user.save()


def FixDuplicateDocumentNaming(request):
    wells = [
        #"BURUNGA 2",
        #"BURUNGA 2A",
        #"BURUNGA LANE 4",
        #"BURUNGA LANE 5",
        #"BURUNGA LANE 6",
        #"PEAT 1",
        #"PEAT 10",
        #"PEAT 15",
        #"PEAT 16",
        #"PEAT 444",
        #"PEAT 45",
        #"PEAT 46",
        #"PEAT 47",
        #"SCOTIA 34",
        #"SCOTIA 35",
        #"SCOTIA 44",
        #"SCOTIA 45",
        #"SOUTH BURUNGA 2",
        "POLARIS 140",
        "POLARIS 142",
        "POLARIS 150",
        "ACRUX 144",
        "ACRUX 145",
        #"ACRUX 146",
    ]
    for well_name in wells:
        myfun(Document.objects.filter(well__well_name__iexact=well_name).order_by('gov_id'))

    return HttpResponse("done")

def myfun(documents):
    for document in documents:
        # Rename if same name
        duplicates = Document.objects.filter(well=document.well,document_name=document.document_name).exclude(id=document.id).all()
        count = Document.objects.filter(well=document.well,document_name=document.document_name).exclude(id=document.id).count()
        if count > 0:
            i = 0
            for duplicate in duplicates:
                i += 1
                name = f"{duplicate.document_name} ({i})"
                log.info('renaming document: %i to %s.', duplicate.id, name)
                duplicate.document_name = name
                duplicate.save()

                if duplicate.file:
                    if duplicate.file == document.file:
                        duplicate.file = None
                        duplicate.status = duplicate.MISSING
                        duplicate.save()
                    else:
                        file = duplicate.file
                        file.file_name = CleanStr(name)
                        file.save()

        # Redownload Documents
        if document.file:
            file = document.file
            result = fileModule.MakeDirectoryForFile(document)
            if result.code != "00000":
                return result
            
            destination = result.destination

            url = CleanURL(document.url)
            fileType = file.file_ext
            name = CleanStr(file.file_name)
            fileName = name + fileType

            # Download File.    
            result = fileModule.downloadFile(url, destination, fileName, True)
            if result.code != "00000":
                return result
        else:
            if document.status == document.DOWNLOADED:
                document.status = document.MISSING
                document.save()
        

    return
