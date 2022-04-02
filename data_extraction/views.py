# Django imports.
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import logout

# Third party imports.
import json

# This module imports.
from .models import *
from .functions import fileSizeAsText, getDocumentTextAsPagesObject, isValidEmail
from .forms import WellFilter
from . import tasks

# Other module imports.
from api import internalAPI
from file_manager import fileModule, convertToJPEG, fileBuckets
from interpretation import googleText



# Logout.
def logout_view(request):
	logout(request)
	return render(request, "public/logout.html")

# Index.
@login_required
def index(request):
	return render(request, "data/index.html")

# Well Search.
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

			wellData = internalAPI.WellSearch(wellName, owner, stateName, permit, statusName, className, purposeName,
				lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
				orderBy, start, end)
	else:
		wellData = internalAPI.WellSearch(None, None, None, None, None, None, None,
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

# File Search.
@login_required
def lasFiles(request):
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

			wellData = internalAPI.LASsearch(wellName, owner, stateName, permit, statusName, className, purposeName,
				lat_min, lat_max, long_min, long_max, rig_release_start, rig_release_end, 
				orderBy, start, end)
	else:
		wellData = None
		#wellData = internalAPI.LASsearch(None, None, None, None, None, None, None,
		#		None, None, None, None, None, None, 
		#		None, 0, 20)
		form = WellFilter()
		
		page = 0
		show_qty = 20
		orderBy = "id"

	# File Bucket
	fileBucket = UserFileBucket.objects.filter(user=request.user).first()
	
	if(fileBucket is None):
		fileBucketFiles = 0
	else:
		fileBucketFilesQuery = FileBucketFiles.objects.filter(bucket=fileBucket).all()
		fileBucketFiles = fileBucketFilesQuery.count()

	context = {
		"wellData" :  wellData,
		"form" : form,
		"page" : page,
		"show_qty" : show_qty,
		"orderBy" : orderBy,

		"fileBucketFiles" : fileBucketFiles,
	}
	
	return render(request, "data/searchLasFiles.html", context)

# File Bucket.
@login_required
def fileBucketNone(request):
	fileBucket = UserFileBucket.objects.filter(user=request.user).first()

	context = FileBucket(fileBucket)
	context["name"] = "Unsaved File Bucket"
	context["saved"] = False

	return render(request, "data/fileBucket.html", context)

@login_required
def fileBucketID(request, id):
	fileBucket = UserFileBucket.objects.filter(id=id).first()

	context = FileBucket(fileBucket)
	context["name"] = fileBucket.name
	context["saved"] = True
	context["link"] = settings.MEDIA_URL + "file_buckets/" + fileBucket.name + ".zip"

	return render(request, "data/fileBucket.html", context)

@login_required
def FileBucket(fileBucket):
	fileBucketFiles = FileBucketFiles.objects.filter(bucket=fileBucket).all()

	documents = []
	sizeKnown = True
	totalSizeByte = 0
	fileCount = 0
	totalFiles = 0
	for fileBucketFile in fileBucketFiles:
		documentObject = fileBucketFile.document
		totalFiles = totalFiles + 1

		if documentObject.file is not None:
			fileCount = fileCount + 1
			sizeByte = documentObject.file.file_size
			if sizeKnown:
				totalSizeByte = totalSizeByte + sizeByte
			
			sizeText = fileSizeAsText(sizeByte)
			
		else:
			sizeText = "unknown"
			sizeKnown = False

		document = {
			"well":documentObject.well.well_name,
			"name":documentObject.document_name,
			"size":sizeText,
			"ext" : internalAPI.GetDocumentExt(documentObject),
		}

		documents.append(document)

	if(totalFiles != 0):
		progress = str(round(fileCount/totalFiles*100,0)) + "%"
	else:
		progress = None

	if sizeKnown:
		totalSizeText = fileSizeAsText(totalSizeByte)
	else: 
		totalSizeText = "unknown"

	context = {
		"id" : fileBucket.id,
		"documents" : documents,
		"totalSize" : totalSizeText,
		"status" :  dict(fileBucket.STATUS).get(fileBucket.status),
		"progress" : progress,
		"saved" : False,
	}

	return context

# File Bucket - Add to.
@login_required
def saveToFileBucket(request):
	data = json.loads(request.body.decode("utf-8"))

	fileBucket = UserFileBucket.objects.filter(user=request.user).first()
	if(fileBucket is None):
		fileBucket = UserFileBucket.objects.create(user=request.user)

	for documentID in data:
		document = Document.objects.filter(id=documentID).first()

		# Check it is not already added.
		fileBucketFile = FileBucketFiles.objects.filter(bucket=fileBucket, document=document).first()
		if(fileBucketFile is None):
			fileBucketFile = FileBucketFiles.objects.create(bucket=fileBucket, document=document)
	
	fileBucketFiles = FileBucketFiles.objects.filter(bucket=fileBucket).all()

	response = {'count':fileBucketFiles.count()}

	return JsonResponse(response)

# File Bucket - Empty.
@login_required
def emptyFileBucketRequest(request):
	success = emptyFileBucket(request.user)

	if(success):
		fileBucket = UserFileBucket.objects.filter(user=request.user).first()
		if(fileBucket is None):
			response = {'count':0}
			return JsonResponse(response)
		else:
			fileBucketFiles = FileBucketFiles.objects.filter(bucket=fileBucket).all()
			response = {'count':fileBucketFiles.count()}
			return JsonResponse(response)
	else:
		response = {'count':-1}
		return JsonResponse(response)		

def emptyFileBucket(user):
	fileBucket = UserFileBucket.objects.filter(user=user).first()

	if(fileBucket is not None):
		files = FileBucketFiles.objects.filter(bucket=fileBucket).all()
		for file in files:
			file.delete()

	return True

# File Bucket - Save.
@login_required
def saveFileBucket(request):
	userId = request.user.id
	tasks.saveFileBucket.delay(userId)

	response = {'success':True}
	return JsonResponse(response)	

# File Bucket - Delete.
@login_required
def deleteFileBucket(request, id):
	fileBucket = UserFileBucket.objects.filter(id=id).first()

	filePath = 'file_buckets/' + fileBucket.name + '.zip'
	
	tasks.deleteFileBucket.delay(filePath, settings.USE_S3)

	fileBucket.delete()

	return redirect('profile')

# API.
#@login_required
def api(request):
	return render(request, "data/api.html")

# Profile.
@login_required
def Profile(request):
	userProfile = UserProfile.objects.filter(user__id = request.user.id).first()

	privileges = dict(UserProfile.PRIVILEGE)
	privilege = privileges[userProfile.privilege]

	if userProfile.privilege == UserProfile.ADMIN:
		organisationUsers = UserProfile.objects.filter(organisation = userProfile.organisation).all()
	else:
		organisationUsers = None

	# File buckets.
	fileBuckets = UserFileBucket.objects.filter(user=request.user).order_by("-id")
	bucketCount = fileBuckets.count() - 1
	fileBuckets = fileBuckets[:bucketCount]

	buckets = []
	for bucketObject in fileBuckets:
		documents = []
		sizeKnown = True
		totalSize = 0

		buckerFilesObjects = FileBucketFiles.objects.filter(bucket=bucketObject).all()

		for buckerFilesObject in buckerFilesObjects:
			documentObject = buckerFilesObject.document
			if documentObject.file is not None:
				if sizeKnown:
					totalSize = totalSize + documentObject.file.file_size
					totalSizeText = fileSizeAsText(totalSize)
			else:
				sizeKnown = False
				totalSizeText = "unknown"


			document = {
				"name" : documentObject.document_name,
				"well" : documentObject.well,
				"ext" : internalAPI.GetDocumentExt(documentObject),
			}
			documents.append(document)

		bucket = {
			"id" : bucketObject.id,
			"name" : bucketObject.name,
			"status" : dict(bucketObject.STATUS).get(bucketObject.status),
			"documents" : documents,
			"totalSize" : totalSizeText,
			"link" : settings.MEDIA_URL + "file_buckets/" + bucketObject.name + ".zip",
			"created": bucketObject.date_created.strftime("%d/%m/%Y"),
			"modified": bucketObject.date_modified.strftime("%d/%m/%Y"),
		}
		buckets.append(bucket)

	
	# Response Data.
	context={
		"userProfile" : userProfile,
		"privilege" : privilege,
		"organisationUsers" : organisationUsers,

		"fileBuckets" : buckets,
		"bucketCount" : bucketCount,
	}

	# Return Response.
	return render(request, "data/profile.html", context)

@login_required
def UpdateProfile(request):
	errors = []
	success = False

	if request.method == "POST":
		data = json.loads(request.body.decode("utf-8"))

		# Username
		if 'username' in data:
			username= data['username']
		else:
			username = None

		if username is None:
			errors.append("Username cannot be blank.")
		elif len(username) < 1:
			username = None
			errors.append("Username cannot be blank.")

		# First Name
		if 'first_name' in data:
			firstName= data['first_name']
		else:
			firstName = None

		if firstName is None:
			errors.append("First Name cannot be blank.")
		elif len(firstName) < 1:
			firstName = None
			errors.append("First Name cannot be blank.")

		# Last Name
		if 'last_name' in data:
			lastName= data['last_name']
		else:
			lastName = None
		if lastName is None:
			errors.append("Last Name cannot be blank.")
		elif len(lastName) < 1:
			lastName = None
			errors.append("Last Name cannot be blank.")

		# Email
		if 'email' in data:
			email= data['email']
		else:
			email = None

		if email is None:
			errors.append("Email cannot be blank.")
		elif len(email) < 1:
			email = None
			errors.append("Email cannot be blank.")
		elif not isValidEmail(email):
			email = None
			errors.append("Invalid email address.")

		statusStr = None
		privilegeStr = None
		
		# Check minimum data provided
		if username is None or firstName is None or lastName is None or email is None:
			success = False
		else:
			user = None
			# Check user being edited
			if 'id' in data:
				id= data['id']

				editor = User.objects.filter(id=request.user.id).first()
				editorProfile = UserProfile.objects.filter(user=editor).first()

				# Check priviliges
				if editorProfile.privilege != editorProfile.ADMIN:
					errors.append("User cannot make this change as they do not have admin privileges.")
				else:
					user = User.objects.filter(id=id).first()
					profile = UserProfile.objects.filter(user=user).first()
					
					# Check same company
					if profile.organisation != editorProfile.organisation:
						errors.append("User cannot make this change as they are not apart of the same organisation as the user being edited.")
						user = None

			else:
				user = User.objects.filter(id=request.user.id).first()
				profile = UserProfile.objects.filter(user=user).first()
			
			if user == None:
				success = False
			else:
				# Status
				statuses = dict(UserProfile.STATUS)
				if 'status' in data:
					status= int(data['status'])
					statusStr = str(statuses[status])
				else:
					status = profile.status

				# Privilege
				privileges = dict(UserProfile.PRIVILEGE)
				if 'privilege' in data:
					privilege= int(data['privilege'])
					privilegeStr = str(privileges[privilege])
				else:
					privilege = profile.privilege

				try:
					user.username = username
					user.first_name = firstName
					user.last_name = lastName
					user.email = email
					profile.status = status
					profile.privilege = privilege

					user.save()
					profile.save()

					success = True
				except Exception as e:
					if hasattr(e, 'message'):
						errors.append("Failed to update user object in the database. Error message: " + e.message)
					else:
						errors.append("Failed to update user object in the database. Error message: " + str(e))
						
					success = False
		
	else: 
		success = False
		errors.append("Method not POST")

	# Response
	response = {
		'success' : success,
		'errors' : errors,
		'username' : username,
		'first_name' : firstName,
		'last_name' : lastName,
		'email' : email,
		'status' : statusStr,
		'privilege' : privilegeStr,
	}

	json_resonse = json.dumps(response)
	return HttpResponse(json_resonse)


# Company Profile.
@login_required
def Company(request):
	userProfile = UserProfile.objects.filter(user__id=request.user.id).first()

	privileges = dict(UserProfile.PRIVILEGE)
	privilege = privileges[userProfile.privilege]

	if userProfile.privilege == UserProfile.ADMIN:
		organisationUsersQuery = UserProfile.objects.filter(organisation = userProfile.organisation).all()

		organisationUsers = []
		statuses = dict(UserProfile.STATUS)
		for otherProfile in organisationUsersQuery:
			organisationUser = {
				"id" : otherProfile.user.id,
				"username" : otherProfile.user.username,
				"first_name" : otherProfile.user.first_name,
				"last_name" : otherProfile.user.last_name,
				"email" : otherProfile.user.email,
				"status" : statuses[otherProfile.status],
				"privilege" : privileges[otherProfile.privilege],
			}

			organisationUsers.append(organisationUser)
	else:
		organisationUsers = None




	# Response Data.
	context={
		"userProfile" : userProfile,
		"privilege" : privilege,
		"organisationUsers" : organisationUsers,
	}

	return render(request, "data/company.html", context)

# Well Details.
@login_required
def details(request, id):
	wellData = internalAPI.retrieveId(id)

	context = {
		"well" :  wellData,
	}
	return render(request, "data/details.html", context)








