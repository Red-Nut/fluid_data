from django.shortcuts import render, HttpResponse

import json
from dateutil.parser import *

from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose

# Create your views here.
def index(request):
    return HttpResponse("API is running")

