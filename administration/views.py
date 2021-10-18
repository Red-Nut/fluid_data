from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from data_extraction.models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose
from data_extraction import myExceptions
from search import config_search
from file_manager import downloader, convertToJPEG
from interpretation import googleText



import json
import time

# Create your views here.

def index(request):
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

def search(request):
	return render(request, "administration/search.html")

def UpdateCompanies(request):
	wells = Well.objects.all()

	for well in wells:
		owner = well.owner.company_name

		newOwner = None

		for correction in config_search.ownerCorrections:
			if owner == correction[0]:
				newOwner = correction[1]

		# Select or create the company object.
		if(newOwner is not None):
			company = Company.objects.filter(company_name=newOwner).first()
			if (company is None):
				try:
					company = Company.objects.create(company_name = newOwner)
				except:
					# Handle Error
					print("Failed to create new company.")
					return
			
			# Assign company to well.
			well.owner = company
			well.save()

			# Check if old company can be deleted.
			check = Well.objects.filter(owner__company_name=owner).first()

			if(check is None):
				# Delete old company object
				oldCompany = Company.objects.filter(company_name=owner).first()
				try:
					oldCompany.delete()
				except:
					print("Failed to delete company: " + owner)



	return HttpResponse("Update Complete")

def DownloadAllMissing(request):
	documents = Document.objects.filter(status=1).all()

	results=DownloadMissingFiles(documents)

	json_resonse = json.dumps(results)
	return HttpResponse(json_resonse)

def DownloadAllWCRs(request):
    documents = Document.objects.filter(status=1).all()
    documents = documents.filter(report__report_type__type_name="Well Completion Report").all()
    documents = documents.filter(Q(url__icontains=".pdf")| Q(url__icontains='.tiff') | Q(url__icontains='.tif') | Q(url__icontains='.las')).all()
    print(documents.count())
	
    results=DownloadMissingFiles(documents)

    json_resonse = json.dumps(results)
    return HttpResponse(json_resonse)

def DownloadMissingFiles(documents):
    results=[]
    for document in documents:
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
            result = downloader.downloadWellFile(document)
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

def GoogleText(request):
	documents = Document.objects.filter(converted=True).all()

	for document in documents:
		result = googleText.getDocumentText(document)

	return HttpResponse("done")