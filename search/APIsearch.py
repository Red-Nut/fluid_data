from . import config_search
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose

import requests
#from bs4 import BeautifulSoup #pip install beautifulsoup4
from json import JSONEncoder
import json
from datetime import datetime

# Error codes.
from data_extraction import myExceptions

def wellExists(wellName):
    well = Well.objects.filter(well_name=wellName).first()
    if (well is None):
        return False
    else:
        return True

class RetriveQLD:
    def __init__(self, id):
        self.id = id
        self.wellName = ""
        self.state = State.objects.filter(name_short="QLD").first()
        self.errors = []
        self.success = None

    def retrive(self):
        # Construct the query.
        query = config_search.api + 'package_show?'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        
        # Make the get request and store it in the response object.
        APIresponse = requests.get(query, headers=headers,params=dict(id=self.id))

        # Construct the query.
        #query = config_search.api + 'package_show?'

        # Make the get request and store it in the response object.
        #APIresponse = requests.get(query,params=dict(id=self.id))

        try:
            #json_response = APIresponse.json()
            json_response = json.loads(APIresponse.content.decode("utf-8"))
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            # Handle Error
            self.success = False
            error = myExceptions.searchList[0]
            print(f"Error {error.code}: {error.consolLog}")
            self.errors.append(error)
            return

        success = json_response["success"]

        if(success != True):
            # Handle Error
            self.success = False
            error = myExceptions.searchList[1]
            print(f"Error {error.code}: {error.consolLog}")
            self.errors.append(error)
            return
        else:
            result = json_response['result']
            resources = result['resources']

            print(result)

            # Get the type.
            type = result.get('type', None)

            # Report type. 
            reportTypeStr = RemoveLink(result.get('georesource_report_type', None),'georesource-report/')
            

            # Create the well class object.
            if(reportTypeStr is not None):
                reportTypeStr = reportTypeStr.replace("-"," ").title()
                reportType = ReportType.objects.filter(type_name=reportTypeStr).first()
                if (reportType is None):
                    try:
                        reportType = ReportType.objects.create(type_name = reportTypeStr)
                    except:
                        # Handle Error
                        self.success = False
                        error = myExceptions.searchList[19]
                        print(f"Error {error.code}: {error.consolLog}")
                        self.errors.append(error)
                        return
            else: 
                reportType = None

            if(reportType is not None):
                if(type == 'magnetic' or 
                type == 'radiometric' or 
                reportType.type_name == "Permit Report Six Month" or 
                reportType.type_name == "Permit Report Annual" or 
                reportType.type_name == "Permit Report Final" or 
                reportType.type_name == "Permit Report Partial Relinquishment" or 
                reportType.type_name == "Seismic Survey Report Final" or 
                reportType.type_name == "Any Other Report"):
                    # Handle Error
                    self.success = False
                    error = myExceptions.searchList[5]
                    print(f"Error {error.code}: {error.consolLog}")
                    self.errors.append(error)
                    return

            # Gov ID.
            gov_id = result.get('name', None)

            # Permit.
            permitStr = result.get('resource_authority_permit', None).upper()
            permitStr = permitStr.replace(" ", "")

            # Create the permit object.
            if(permitStr is not None):
                permit = Permit.objects.filter(permit_number=permitStr).first()
                if (permit is None):
                    try:
                        permit = Permit.objects.create(permit_number = permitStr)
                    except Exception as e:
                        # Handle Error
                        self.success = False
                        error = myExceptions.searchList[21]
                        error.consolLog = error.consolLog + " Permit: " + permitStr
                        print(f"Error {error.code}: {error.consolLog}")
                        #raise e
                        self.errors.append(error)
                        return
            else:
                permit = None

            # Well name.
            title = result.get('title', None)
            permitStr = result.get('resource_authority_permit', None)
            if(title is not None) and permitStr is not None:
                wellName = GetWellName(title,str(permitStr))
            else: 
                wellName = None

            self.wellName = wellName

            # Owner.
            owner = result.get('owner', 'None').title()
            if(owner == 'None'):
                owner = result.get('operator', 'None').title()

            # Owner corrections
            for correction in config_search.ownerCorrections:
                if owner == correction[0]:
                    owner = correction[1]

            if(owner == 'None'):
                owner = None

            # Create the company object.
            if(owner is not None):
                company = Company.objects.filter(company_name=owner).first()
                if (company is None):
                    try:
                        company = Company.objects.create(company_name = owner)
                    except:
                        # Handle Error
                        self.success = False
                        error = myExceptions.searchList[10]
                        print(f"Error {error.code}: {error.consolLog}")
                        self.errors.append(error)
                        return
            else:
                company = None

            # Status. 
            statusStr = result.get('state', None).title()

            # Create the well status object.
            if(statusStr is not None):
                status = WellStatus.objects.filter(status_name=statusStr).first()
                if (status is None):
                    try:
                        status = WellStatus.objects.create(status_name = statusStr)
                    except:
                        # Handle Error
                        self.success = False
                        error = myExceptions.searchList[18]
                        print(f"Error {error.code}: {error.consolLog}")
                        self.errors.append(error)
                        return
            else:
                status = None

            # Well Class.
            wellClassStr = RemoveLink(result.get('borehole_class', None),"resource-project-lifecycle/")
            
            # Create the well class object.
            if(wellClassStr is not None):
                wellClassStr = wellClassStr.replace("-"," ").title()
                wellClass = WellClass.objects.filter(class_name=wellClassStr).first()
                if (wellClass is None):
                    try:
                        wellClass = WellClass.objects.create(class_name = wellClassStr)
                    except:
                        # Handle Error
                        self.success = False
                        error = myExceptions.searchList[16]
                        print(f"Error {error.code}: {error.consolLog}")
                        self.errors.append(error)
                        return
            else: 
                wellClass = None

            # Well Purpose.
            wellPurposeStr = RemoveLink(result.get('borehole_purpose', None),"borehole-purpose/")

            # Create the well purpose object.
            if(wellPurposeStr is not None):
                wellPurposeStr = wellPurposeStr.replace("-"," ").title()
                purpose = WellPurpose.objects.filter(purpose_name=wellPurposeStr).first()
                if (purpose is None):
                    try:
                        purpose = WellPurpose.objects.create(purpose_name = wellPurposeStr)
                    except:
                        # Handle Error
                        self.success = False
                        error = myExceptions.searchList[17]
                        print(f"Error {error.code}: {error.consolLog}")
                        self.errors.append(error)
                        return
            else: 
                purpose = None
            
            # Geodata (Not used yet).
            GeoJSONextent = result.get('GeoJSONextent', None)

            # Latitude and Longitude.
            try:
                GeoData = json.loads(GeoJSONextent)
                if(GeoData['type'] == "Point"):
                    lat = GeoData['coordinates'][1]
                    long = GeoData['coordinates'][0]
                elif(GeoData['type'] == "Polygon"):
                    myCoords = GeoData['coordinates'][0]
                    x = 0
                    lat = 0.0
                    long = 0.0
                    for point in myCoords:
                        x = x + 1
                        lat = lat + float(point[1])
                        long = long + float(point[0])
                    if(x>0):
                        lat = lat/x
                        long = long/x
                    else: 
                        lat = None
                        long = None
                else:
                    lat = None
                    long = None
            except:
                lat = None
                long = None

            # Rig Release.
            rigReleaseStr = result.get('rig_release_date', None)
            rigRelease = config_search.ConvertQLDDate(rigReleaseStr)

            # Modified.
            modifiedStr = result.get('metadata_modified', None)
            modified = config_search.ConvertQLDDateTime(modifiedStr)

            # Check if well already exists
            well = Well.objects.filter(well_name=wellName).first()
            if (wellExists(wellName)):
                # Handle Error
                #self.success = False
                #error = myExceptions.searchList[12]
                #print(f"Well '{wellName}' already exists in database.")
                #self.errors.append(error)

                # Update values.

                # Update id if object is the borehole
                if(type == "borehole"):
                    well.gov_id=gov_id
                
                
                if(modified > well.modified):
                    # Update values if modified date is greater.
                    if(company is not None):
                        well.owner = company
                    if(status is not None):
                        well.status = status
                    if(wellClass is not None):
                        well.well_class = wellClass
                    if(purpose is not None):
                        well.purpose = purpose
                    if(permit is not None):
                        well.permit = permit
                    if(lat is not None):
                        well.latitude = lat
                    if(long is not None):
                        well.longitude = long
                    if(rigRelease is not None):
                        well.rig_release = rigRelease
                                                
                    well.modified = modified
                else:
                    # Update any null values.
                    if(well.owner is None and company is not None):
                        well.owner = company
                    if(well.status is None and status is not None):
                        well.status = status
                    if(well.well_class is None and wellClass is not None):
                        well.well_class = wellClass
                    if(well.purpose is None and purpose is not None):
                        well.purpose = purpose
                    if(well.permit is None and permit is not None):
                        well.permit = permit
                    if(well.latitude is None and lat is not None):
                        well.latitude = lat
                    if(well.longitude is None and long is not None):
                        well.longitude = long
                    if(well.rig_release is None and rigRelease is not None):
                        well.rig_release = rigRelease
                

                # Save the updated records
                try:
                    well.save()
                except Exception as e:
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    # Handle Error
                    self.success = False
                    error = myExceptions.searchList[20]
                    print(f"Error {error.code}: {error.consolLog}")
                    self.errors.append(error)
                    return
            else:
                try:
                    well = Well.objects.create(
                        gov_id = gov_id,
                        well_name = wellName,
                        owner = company,
                        state = self.state,
                        status = status,
                        well_class = wellClass,
                        purpose = purpose,
                        permit = permit,
                        latitude = lat,
                        longitude = long,
                        rig_release = rigRelease,
                        modified = modified
                    )
                except Exception as e:
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    # Handle Error
                    self.success = False
                    error = myExceptions.searchList[11]
                    print(f"Error {error.code}: {error.consolLog}")
                    self.errors.append(error)
                    return



            # RESOURCES
            if(type == "borehole"):
                for resource in resources:
                    # Check if resource is active.
                    if (resource['state'] == "active"):

                        # Document Name.
                        documentName = resource['name']
                        
                        # URL.
                        url = resource['url']

                        # Check if document exists.
                        document = Document.objects.filter(well=well,document_name=documentName).first()
                        if(document is None):
                            try:
                                document = Document.objects.create(
                                    document_name = documentName,
                                    well=well,
                                    url = url
                                )
                            except:
                                # Handle Error.
                                self.success = False
                                error = myExceptions.searchList[14]
                                error.consolLog = error.consolLog + " Well: " + well.well_name + " Document: " + documentName
                                print(f"Error {error.code}: {error.consolLog}")
                                self.errors.append(error)
                        else:
                            # Handle Error.
                            self.success = False
                            error = myExceptions.searchList[15]
                            error.consolLog = error.consolLog + " Well: " + well.well_name + " Document: " + documentName
                            print(f"Error {error.code}: {error.consolLog}")
                            self.errors.append(error)

            elif (type == "report"):
                # Create the report object.
                creator = result.get('creator', None)

                metadata_modified_str = result.get('metadata_modified', None)
                metadata_modified = config_search.ConvertQLDDateTime(metadata_modified_str)

                metadata_created_str = result.get('metadata_created', None)
                metadata_created = config_search.ConvertQLDDateTime(metadata_created_str)

                dataset_completion_date_str = result.get('dataset_completion_date', None)
                dataset_completion_date = config_search.ConvertQLDDate(dataset_completion_date_str)

                open_file_date_str = result.get('open_file_date', None)
                open_file_date = config_search.ConvertQLDDate(open_file_date_str)

                urlType = result.get('type', None)
                if(urlType is not None and id is not None):
                    reportUrl = config_search.urlBase + '/' + urlType + '/' + gov_id
                else:
                    reportUrl = None

                if(reportType.type_name == "Well Completion Report"):
                    reportTitle = "Well Completion Report: " + well.well_name
                else:
                    reportTitle = title

                # Check if report exists.
                report = Report.objects.filter(well=well,gov_id=gov_id).first()
                if(report is None):
                    report = Report.objects.create(
                        well=well, 
                        url=reportUrl,
                        gov_id = gov_id,
                        gov_report_name=title,
                        gov_creator=creator,
                        gov_created=metadata_modified,
                        gov_modified=metadata_created,
                        gov_dataset_completion_date=dataset_completion_date,
                        gov_open_file_date=open_file_date,
                        report_name=reportTitle,
                        report_type = reportType,
                    )

                for resource in resources:
                    # Check if resource is active.
                    if (resource['state'] == "active"):

                        # Document Name.
                        documentName = resource['name']
                        
                        # URL.
                        url = resource['url']

                        # Check if document exists.
                        document = Document.objects.filter(well=well,document_name=documentName).first()
                        if(document is None):
                            try:
                                document = Document.objects.create(
                                    document_name = documentName,
                                    well=well,
                                    url = url,
                                    report=report
                                )
                            except:
                                # Handle Error.
                                self.success = False
                                error = myExceptions.searchList[14]
                                print(f"Error {error.code}: {error.consolLog}")
                                self.errors.append(error)
                        else:
                            # Handle Error.
                            self.success = False
                            error = myExceptions.searchList[15]
                            print(f"Error {error.code}: {error.consolLog}")
                            print("Well: " + str(well))
                            print("Document: " + documentName)
                            self.errors.append(error)
            else:
                pass

            # Confirm the success or failure of adding the well.
            if(self.success is None):
                if len(self.errors) == 0:
                    self.success = True
                else: 
                    self.success = False

                

                


            

class SearchQLD:
    def __init__(self, searchString, attachmentsOnly, WCRonly, includeExisting):
        self.searchString = searchString
        self.attachmentsOnly = attachmentsOnly
        self.WCRonly = WCRonly
        self.includeExisting = includeExisting
        self.results = []
        self.errors = []

class WebScrapeSearchQLD(SearchQLD):
    def __repr__(self):
        str = "Search Method: WebScrape, Search String: {}\n" 
        str =str.format( self.searchString)
        return str

class APISearchQLD(SearchQLD):
    def search(self):
        # Construct the query.
        query = config_search.api + 'package_search?q='+self.searchString+'&rows='+config_search.maxRows
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        
        # Make the get request and store it in the response object.
        APIresponse = requests.get(query, headers=headers)

        # Convert the payload as JSON
        try:
            json_response = json.loads(APIresponse.content.decode("utf-8"))
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
            # Handle Error
            self.success = False
            error = myExceptions.searchList[0]
            print(f"Error {error.code}: {error.consolLog}")
            self.errors.append(error)
            return
        #print(json_response)
        success = json_response["success"]

        if(success != True):
            # Handle Error
            self.success = False
            error = myExceptions.searchList[1]
            print(f"Error {error.code}: {error.consolLog}")
            self.errors.append(error)
            return
        else:
            # Cycle through search results.
            for result in json_response['result']['results']:
                #print(result)
                # Create the result object
                myID = result.get('id', 'None')
                if(myID != 'None'):
                    myResult = Result(myID)
                    
                    # Get the number of resources.
                    myResult.num_resources = int(result.get('num_resources', 0))
                    # Get the report type.
                    georesource_report_type = RemoveLink(result.get('georesource_report_type', 'None'),'georesource-report/')

                    #Perform checks on resouce count (results with attachments only) and report type (WCRs only).
                    if((myResult.num_resources > 0 or self.attachmentsOnly == False) and \
                        (georesource_report_type == 'well-completion-report' or self.WCRonly == False)):

                        # Get general data.
                        myResult.name = result.get('name', 'None')
                        myResult.title = result.get('title', 'None')
                        myResult.type = georesource_report_type.replace('-'," ").title()
                        myResult.owner = result.get('owner', 'None').title()
                        myResult.permit = result.get('resource_authority_permit', 'None')
                        myResult.GeoJSONextent = result.get('GeoJSONextent', 'None')
                        myResult.wellName = GetWellName(myResult.title,myResult.permit)
                        myResult.state = "QLD"

                        # Get data about the record
                        myResult.status = result.get('state', 'None')
                        myResult.metadata_modified = result.get('metadata_modified', 'None')
                        myResult.metadata_created = result.get('metadata_created', 'None')
                        myResult.dataset_completion_date = result.get('dataset_completion_date', 'None')
                        myResult.open_file_date = result.get('open_file_date', 'None')
                        myResult.creator = result.get('creator', 'None')

                        # Does the well exists in the database
                        myResult.existsInDatabase = wellExists(myResult.wellName)

                        # Get the resourc list
                        resources = result.get('resources', 'None')
                        if(resources != 'None'):
                            myResult.resources = resources

                        # Check if resources before adding well.
                        if(resources != 'None' or not self.attachmentsOnly):
                            # Check if record exists in database before adding.
                            well = Well.objects.filter(well_name = myResult.wellName).first()
                            if(well is None or self.includeExisting):
                                self.results.append(myResult)
                                self.success = True

                        

    
    


    def __repr__(self):
        str = "Search Method: API, Search String: {}\n" 
        str =str.format( self.searchString)
        return str

class Result:
    def __init__(self,id):
        self.id = id
        self.num_resources = 0
        self.resources = []

    def __repr__(self):
        str = "Title: {}\n" 
        str =str.format( self.title)
        return str

class ResultEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def RemoveLink(mstr, subFolder):
    if(mstr is not None):
        x = mstr.find("http://linked.data.gov.au/def/" + subFolder)
        if(x > -1):
            mstr = mstr[x+30 + len(subFolder):]
    
    return mstr
    

def GetWellName(title, permit):
        wellName = title

        # Remove permit.
        if(permit + "," in wellName):
            x = wellName.find(permit + ",")
            wellName = wellName[:x] + wellName[x+len(permit)+1:]
            wellName = wellName.strip()

        # Remove company.
        x = wellName.find(" ")
        if(x == 3):
            wellName = wellName[3:]
            wellName = wellName.strip()

        # Remove additonal.
        x = wellName.find(",")
        if(x != -1):
            wellName = wellName[:x]
            wellName = wellName.strip()
        else: 
            # If no comma found, find the a numeral and then find the next space.
            a = 999
            b = wellName.find("1")
            a = b if b<a and b!=-1 else a
            b = wellName.find("2")
            a = b if b<a and b!=-1 else a
            b = wellName.find("3")
            a = b if b<a and b!=-1  else a
            b = wellName.find("4")
            a = b if b<a and b!=-1  else a
            b = wellName.find("5")
            a = b if b<a and b!=-1  else a
            b = wellName.find("6")
            a = b if b<a and b!=-1  else a
            b = wellName.find("7")
            a = b if b<a and b!=-1  else a
            b = wellName.find("8")
            a = b if b<a and b!=-1  else a
            b = wellName.find("9")
            a = b if b<a and b!=-1  else a
            if(a != -1 and a != 999):
                x = wellName.find(" ",a)
                if(x != -1):
                    wellName = wellName[:x]
                    wellName = wellName.strip()

        # Title case.
        x = wellName.split()
        wellName = ""
        for y in x:
            if not y[0].isdigit():
                y = y.title()
            wellName += y + " "

        return wellName.strip()