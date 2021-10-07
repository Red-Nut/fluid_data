
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q

from search import config_search
from api import internalAPI
from file_manager import downloader, convertToJPEG

from .models import Company, Data, Document, File, Page, Report, State, WellStatus, Well
from .forms import WellFilter
from . import myExceptions

import json
import time

def index(request):
	if request.method == "POST":
		form = WellFilter(request.POST)

		if form.is_valid():
			wellName = form.cleaned_data['well_name']
			owner = form.cleaned_data['owner']
			
			state = form.cleaned_data['state']
			if(state is not None):
				stateName = state.name_long
			else:
				stateName = None

			permit = form.cleaned_data['permit']

			status = form.cleaned_data['status']
			if(status is not None):
				statusName = status.status_name
			else:
				statusName = None

			wellClass = form.cleaned_data['wellClass']
			if(wellClass is not None):
				className = wellClass.class_name
			else:
				className = None

			purpose = form.cleaned_data['purpose']
			if(purpose is not None):
				purposeName = purpose.purpose_name
			else:
				purposeName = None

			lat_min = form.cleaned_data['lat_min']
			lat_max = form.cleaned_data['lat_max']
			long_min = form.cleaned_data['long_min']
			long_max = form.cleaned_data['long_max']
			rig_release_start = form.cleaned_data['rig_release_start']
			rig_release_end = form.cleaned_data['rig_release_end']

			orderBy = form.cleaned_data['orderBy']
			page = form.cleaned_data['page']
			#Show_qty can be 20, 50, 100
			show_qty = form.cleaned_data['show_qty']
			#print("Page: " + str(page))
			#print("Qty: " + str(show_qty))

			if(page != None and page != '' and show_qty != None and show_qty != ''):
				start = page*show_qty
				end = (page+1)*show_qty
			else:
				start = 0
				end = 20

			#print("Start: " + str(start))
			#print("End: " + str(end))

			wellData = internalAPI.search(wellName, owner, stateName, permit, statusName, className, purposeName,
				lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
				orderBy, start, end)
	else:
		wellData = internalAPI.search(None, None, None, None, None, None, None,
				None, None, None, None, None, None, 
				None, 0, 20)
		form = WellFilter()
		
		page = 0
		show_qty = 20
		orderBy = "id"

	context = {
		"wellData" :  wellData,
		"form" : form,
		"page" : page,
		"show_qty" : show_qty,
		"orderBy" : orderBy,
	}

	
	return render(request, "data/index.html", context)

def search(request):
	return render(request, "administration/search.html")

def details(request, id):
	wellData = internalAPI.retrieveId(id)

	context = {
		"well" :  wellData,
	}
	return render(request, "data/details.html", context)


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
	#print(documents.count())
	documents = documents.filter(report__report_type__type_name="Well Completion Report").all()
	#print(documents.count())
	documents = documents.filter(Q(url__icontains=".pdf")| Q(url__icontains='.tiff') | Q(url__icontains='.tif') | Q(url__icontains='.las')).all()
	print(documents.count())
	
	results=DownloadMissingFiles(documents)

	json_resonse = json.dumps(results)
	return HttpResponse(json_resonse)

def DownloadMissingFiles(documents):
	results=[]
	for document in documents:
		print(document.report.report_name)
		url = document.url

		if url is None :
			document.status = 3
			document.save()
		elif "report geometry" in document.document_name.lower() or "ocr extract of report" in document.document_name.lower():
			document.status = 3
			document.save()
		else: 
			#print("DOWNLOADING FILE - Well: " + document.well.well_name + " File: " + document.document_name)
			result = downloader.downloadFile(document)
			if result.code == "50000":
				try:
					file = File.objects.create(
						file_name = result.file_name,
						file_ext = result.file_ext,
						file_location = result.file_location,
						file_size = result.file_size
					)
					document.file = file
					document.status = 2
					document.save()

				except Exception as e:
					result = myExceptions.downloadList[3]
					result.description = result.description + ". Well: " + document.well.well_name + ". Document: " + document.document_name
					result.consolLog = result.consolLog + ". Well: " + document.well.well_name + ". Document: " + document.document_name
					print(result.consolLog)
					#raise e

			results.append(result.description)
			time.sleep(0.2)
		
	return results

def ConvertAllMissingToJPEG(request):
	documents = Document.objects.filter(converted=False).all()
	documents = documents.filter(status=2).all()
	documents = documents.filter(Q(file__file_ext='.pdf') | Q(file__file_ext='.tiff') | Q(file__file_ext='.tif')).all()

	results=[]

	for document in documents:
		path = document.file.file_location + document.file.file_name + document.file.file_ext
		print(path)
		result = convertToJPEG.convertFile(path)
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