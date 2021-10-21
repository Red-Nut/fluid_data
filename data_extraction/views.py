
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q

from search import config_search
from api import internalAPI
from file_manager import downloader, convertToJPEG
from interpretation import googleText

from .models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose
from .forms import WellFilter
from . import myExceptions

import json
from json import JSONEncoder
import jsonpickle
import time

@login_required
def index(request):
	return render(request, "data/index.html")

@login_required
def search(request):
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

	
	return render(request, "data/search.html", context)

@login_required
def api(request):
	return render(request, "data/api.html")

@login_required
def profile(request):
	return render(request, "data/profile.html")

@login_required
def company(request):
	return render(request, "data/company.html")

def details(request, id):
	wellData = internalAPI.retrieveId(id)

	context = {
		"well" :  wellData,
	}
	return render(request, "data/details.html", context)




def getDocumentText(document):
	pageObjects = Page.objects.filter(document=document).order_by("page_no")

	pages = []
	for pageObject in pageObjects:
		texts = Text.objects.filter(
				page = pageObject
			).order_by(
				"BoundingPolys__y", "BoundingPolys__x"
			).all()

		page = {page:pageObject,texts:texts}

		pages.append(page)

	return pages

	