import requests
import urllib.request
import time
import os
from bs4 import BeautifulSoup #pip install beautifulsoup4
from termcolor import colored #pip install termcolor
import urllib.request
import shutil
import json

os.system('color')


#DOWNLOAD FOLDER
pathDownload = 'G:\\WCR'

searchString = input('    Enter Search String:')

#Attachments Only?
noAttachments = False
r = input('    Would you like to view reports without attachments? (Y/N):')
while r not in ('Y','N','y','n'):
	print('Please type "Y" or "N"')
	r = input()
if(r == 'N' or r == 'n'):
	noAttachments = True
elif(r != 'Y' and r != 'y'):
	print(colored('error','red'))
	exit()
else:
	noAttachments = False

#Well Completion Reports Only?
noWCR = False
r = input('    Would you like to view reports that are not Well Completion Reports? (Y/N):')
while r not in ('Y','N','y','n'):
	print('Please type "Y" or "N"')
	r = input()
if(r == 'N' or r == 'n'):
	noWCR = True
elif(r != 'Y' and r != 'y'):
	print(colored('error','red'))
	exit()
else:
	noWCR = False





def main(input):
	# set the API endpoint
	api = 'https://geoscience.data.qld.gov.au/api/action/'

	# construct our query
	query = api + 'package_search?q='+input+'&rows=99999'

	getResultsList(query)

	downloadResults()


def getResultsList(query):
	# make the get request and store it in the response object
	response = requests.get(query)

	# view the payload as JSON
	json_response = response.json()
	print("Success:" + str(json_response['success']))
	print("Result Count: " + str(json_response['result']['count']))
	print("Sort: " + json_response['result']['sort'])

	print('\r\n')
	i = 1
	for result in json_response['result']['results']:
		myResult = Result()

		myResult.resourceCount = int(result.get('num_resources', 0))
		myResult.title = result.get('title', 'None')
		myResult.bClass = removeLink(result.get('borehole_class', 'None'), 'resource-project-lifecycle/')
		myResult.bPurp = removeLink(result.get('borehole_purpose', 'None'), 'borehole-purpose/')

		if((myResult.resourceCount > 0 or noAttachments == False) and \
			(('well completion report' in myResult.title.lower()) or myResult.bClass != "None" or (myResult.bPurp != "None" and myResult.bPurp.lower() != "water") or \
			noWCR == False)):

			print(colored('Result ID: ' + str(i), 'yellow'))
			#print(result)
			myResult.id = saveAndPrint(result.get('id', 'None'), 'ID', 'white')
			myResult.title = saveAndPrint(result.get('title', 'None'), 'Title', 'white')
			myResult.permit = saveAndPrint(result.get('resource_authority_permit', 'None'), 'Permit', 'white')
			myResult.status = saveAndPrint(removeLink(result.get('status', 'None'), 'site-status/'), 'Status', 'white')
			myResult.bClass = saveAndPrint(removeLink(result.get('borehole_class', 'None'), 'resource-project-lifecycle/'), 'Borehole Class', 'white')
			myResult.bPurp = saveAndPrint(removeLink(result.get('borehole_purpose', 'None'), 'borehole-purpose/'), 'Borehole Purpose', 'white')
			myResult.bSub = saveAndPrint(removeLink(result.get('borehole_sub_purpose', 'None'), 'borehole-sub-purpose/'), 'Borehole Sub-Purpose', 'white')
			myResult.maintainer = saveAndPrint(result.get('maintainer', 'None'), 'Maintainer', 'white')
			myResult.operator = saveAndPrint(result.get('operator', 'None'), 'Operator', 'white')
			myResult.rigDate = saveAndPrint(result.get('rig_release_date', 'None'), 'Rig Release Date', 'white')
			#geoData = saveAndPrint(result.get('GeoJSONextent', 'None'), 'GeoJSONextent', 'white')
			#resources = saveAndPrint(result.get('resources', 'None'), 'Resources', 'green')
			#print(colored("    Resources:", 'white'))


			myResult.attachments = []

			resources = result['resources']
			j = 1
			for res in resources:
				att = Attachment()
				#print(res)

				att.name = res.get('name', 'None')
				att.description = res.get('resource:description', 'None')
				att.format = res.get('resource:format', 'None')
				att.type = res.get('resource:resource_type', 'None')
				att.url = res.get('url', 'None')

				print(colored("        Attachment " + str(j) + ":" + att.name + "(" + att.format + ")", 'yellow'))
				#print(colored("        url " + str(j) + ":" + att.url, 'yellow'))

				myResult.attachments.append(att)

				j += 1

			resultList.append(myResult)
			i += 1

def downloadResults():
	print(colored('\r\n    Which files would you like to download?','white'))
	print(colored('        Please enter a comma separated list of result IDs (for example 1,4,6)','white'))
	print(colored('        type "none" or "0" to cancel','white'))
	print(colored('        or type "all" to download all Well Completion Reports.\r\n','white'))
	dWells = input('    :')
	if(dWells.lower() == 'all'):
		for i in range(len(resultList)):
			if('well completion report' in resultList[i].title.lower()):
				download(i)
	elif(dWells.lower() == 'none' or dWells == "0"):
		pass
	else:
		split=dWells.split(',')
		for s in split:
			try:
				i = int(s)
			except ValueError:
				print(colored('    ' + s + ' is not an integer','red'))
				continue

			download(i-1)

	print(colored('\r\nDownloading Complete','Orange'))

def download(i):
	result = resultList[i]
	wellName = result.title
	list = result.attachments

	if(len(list) == 0):
		print(colored("No attachments for result: " + wellName,'yellow'))
	else:
		#remove permit
		if(result.permit + "," in wellName):
			x = wellName.find(result.permit + ",")
			wellName = wellName[:x] + wellName[x+len(result.permit)+1:]
			wellName = wellName.strip()

		#remove company
		x = wellName.find(" ")
		if(x == 3):
			wellName = wellName[3:]
			wellName = wellName.strip()

		#remove additonal
		x = wellName.find(",")
		if(x != -1):
			wellName = wellName[:x]
			wellName = wellName.strip()

		wellName = wellName.replace(" ", "_")
		print(colored('\r\n    Folder Name: ' + wellName,'green'))

		baseFolder = pathDownload + '\\' + wellName

		if(os.path.isdir(baseFolder)):
			print(colored("Skipping: " + result.title + " (Folder '"+ wellName +"' already exists)",'yellow'))
		else:
			print('    Downloading Files for ' + result.title)

			#create folder
			folderSuccess = False
			try:
				print('    Creating Folder: ' + wellName)
				os.mkdir(baseFolder)
				folderSuccess = True
			except Exception as e:
				print(colored('    Unable to create "' + wellName + '" directory', 'red'))
				print(colored(str(e),'red'))
				folderSuccess = False

			if(folderSuccess):
				for j in range(len(list)):
					url = list[j].url

					response = requests.get(url)
					if(response.status_code != 200):
						print(colored('            Connection Failed. Response Code: ' + response.status_code + '\r\n','red'))
					else:
						link = url
						x = len(link) - link.rfind('.')
						fileType = link[-x:]

						name = list[j].name
						name = name.replace("/","")
						name = name.replace(":","")
						name = name.replace("*","")
						name = name.replace("?","")
						name = name.replace('"',"")
						name = name.replace("<","")
						name = name.replace(">","")
						name = name.replace("|","")

						name = name.replace(" ", "_")

						filePath = baseFolder + '\\' + name + fileType
						if(name.find("wireline")>-1 or name.find("cmi")>-1):
							print('        Skipping File: ' + name + fileType)
						else:
							print('        ...Downloading: ' + name + fileType)
							with urllib.request.urlopen(link) as response, open(filePath, 'wb') as out_file:
								shutil.copyfileobj(response, out_file)


						time.sleep(0.2)


def saveAndPrint(mstr, name, colour):
	print(colored('    ' + name + ": " + str(mstr),colour))
	return str(mstr)

def removeLink(mstr, subFolder):
	x = mstr.find("http://linked.data.gov.au/def/" + subFolder)
	if(x > -1):
		mstr = mstr[x+30 + len(subFolder):]
	return mstr

class Result:
	pass
class Attachment:
	pass

resultList = []

main(searchString)
