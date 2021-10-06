from . import config_search
from data_extraction.models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose
from data_extraction.myExceptions import Error, searchList as errorList

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

def Add(wellId,state):
    if state == "QLD":
        myRetrive = RetriveQLD(wellId)
        myRetrive.retrive()

    response = {'success':myRetrive.success,'wellName':myRetrive.wellName,'errors':ResultEncoder().encode(myRetrive.errors)}
    return response

def RetreiveAllQLD(existing):
    state = State.objects.filter(name_short="QLD").first()
    if(state is None):
        state = State.objects.create(name_long = "Queensland", name_short="QLD")

    query = config_search.api + 'package_list'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    APIresponse = requests.get(query, headers=headers)

    try:
        #json_response = APIresponse.json()
        json_response = json.loads(APIresponse.content.decode("utf-8"))
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
        # Handle Error
        error = myExceptions.searchList[0]
        print(f"Error {error.code}: {error.consolLog}")
        return

    success = json_response["success"]

    if(success != True):
        # Handle Error
        error = myExceptions.searchList[1]
        print(f"Error {error.code}: {error.consolLog}")
        return
    else:
        result = json_response['result']

        responseList = []
        #i = 0
        for well in result:
            #if(i < 1000):
            if(existing):
                response = Add(well,"QLD")
                #if response.success == False:
                responseList.append(response)
            else:
                myWell = Well.objects.filter(gov_id=well).first()
                if (myWell is None):
                    response = Add(well,"QLD")
                    responseList.append(response)

                #i = i + 1


        response = {'results':ResultEncoder().encode(responseList)}

        return response


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
            myError = errorList[0]
            error = Error(myError.code,myError.description,myError.consolLog)
            print(f"Error {error.code}: {error.consolLog}")
            self.errors.append(error)
            return

        success = json_response["success"]

        if(success != True):
            # Handle Error
            self.success = False
            myError = errorList[1]
            error = Error(myError.code,myError.description,myError.consolLog)
            print(f"Error {error.code}: {error.consolLog}")
            self.errors.append(error)
            return
        else:
            result = json_response['result']
            resources = result['resources']

            #print(result)

            # Title
            title = result.get('title', None)
            print(title)
            self.wellName = title

            # Get the type.
            type = result.get('type', None)

            # Report type. 
            reportTypeStr = RemoveLink(result.get('georesource_report_type', None),'georesource-report/')

            if(type == 'magnetic' or 
                type == 'radiometric' or
                type == 'seismic' or 
                type == 'map-collection' or 
                type == 'spectral' or 
                type == 'electromagnetic' or 
                type == 'gravity' or 
                type == 'gravity-gradiometry' or  
                type == 'magnetotelluric' or 
                type == 'geochemistry'):
                # Handle Error
                self.success = False
                myError = errorList[5]
                error = Error(myError.code,myError.description,myError.consolLog)
                #print(f"Error {error.code}: {error.consolLog}")
                self.errors.append(error)
                return

            if(reportTypeStr is not None):
                reportTypeStr = reportTypeStr.replace("-"," ").title()

                if(reportTypeStr == "Permit Report Six Month" or 
                reportTypeStr == "Permit Report Annual" or 
                reportTypeStr == "Permit Report Final" or 
                reportTypeStr == "Permit Report Partial Relinquishment" or 
                reportTypeStr == "Seismic Survey Report Final" or 
                reportTypeStr == "Petroleum Report Other" or 
                reportTypeStr == "Petroleum Report Resource And Reserves Information" or 
                reportTypeStr == "Petroleum Report Relinquishment" or 
                reportTypeStr == "Collaborative Exploration Initiative Final" or 
                reportTypeStr == "Geothermal Report Annual Reserves" or 
                reportTypeStr == "Mine Plan Lodgement" or 
                reportTypeStr == "Petroleum Report Cumulative Water Production" or 
                reportTypeStr == "Industry Consultative Report" or 
                reportTypeStr == "Commissioned Industry Study Or Report" or 
                reportTypeStr == "Permit Report Surrender" or 
                reportTypeStr== "Petroleum Report Infrastructure" or 
                reportTypeStr == "Petroleum End Tenure" or 
                reportTypeStr == "Technical Report" or 
                reportTypeStr == "Petroleum End Authority" or 
                reportTypeStr == "Petroleum Report Production Information" or 
                reportTypeStr == "Greenhouse Gas Report Storage Capacity" or 
                reportTypeStr == "Industry Network Initiative Final" or 
                reportTypeStr == "Geological Survey Of Queensland Publication" or 
                reportTypeStr == "Collaborative Drilling Initiative Final" or 
                reportTypeStr == "Queensland Government Mining Journal" or 
                reportTypeStr == "Soil And Land Resources" or 
                reportTypeStr == "Geological Survey Of Queensland Record" or 
                reportTypeStr == "Reserves Petroleum" or 
                reportTypeStr == "Production Petroleum" or 
                reportTypeStr == "Petroleum Report Annual" or 
                reportTypeStr == "Permit Report Final Higher Tenure" or 
                reportTypeStr == "Permit Report Annual Ml" or 
                reportTypeStr == "Permit Report Other" or 
                reportTypeStr == "Geophysical Survey Report Final" or 
                reportTypeStr == "Scientific Or Technical Survey Report" or 
                reportTypeStr == "Permit Report Final Relinquishment" or 
                reportTypeStr == "Seismic Survey Report Reprocessing" or 
                reportTypeStr == "Well Proposal" or 
                reportTypeStr == "Well Report Other" or 
                reportTypeStr == "Any Other Report" or 
                reportTypeStr == "Seismic Survey Report Other" or 
                reportTypeStr == "Permit Report Final" or 
                reportTypeStr == "Petroleum Report Field Information" or 
                reportTypeStr == "Any Other Report"):
                    # Handle Error
                    self.success = False
                    myError = errorList[5]
                    error = Error(myError.code,myError.description,myError.consolLog)
                    #print(f"Error {error.code}: {error.consolLog}")
                    self.errors.append(error)
                    return

            # Create the Report Type object.
            if(reportTypeStr is not None):
                reportTypeStr = reportTypeStr.replace("-"," ").title()
                reportType = ReportType.objects.filter(type_name=reportTypeStr).first()
                if (reportType is None):
                    try:
                        reportType = ReportType.objects.create(type_name = reportTypeStr)
                    except:
                        # Handle Error
                        self.success = False
                        myError = errorList[19]
                        error = Error(myError.code,myError.description,myError.consolLog)
                        print(f"Error {error.code}: {error.consolLog}")
                        self.errors.append(error)
                        return
            else: 
                reportType = None
            
            # Gov ID.
            gov_id = result.get('name', None)
            if(gov_id is None):
                # Handle Error
                self.success = False
                myError = errorList[3]
                error = Error(myError.code,myError.description,myError.consolLog)
                print(f"Error {error.code}: {error.consolLog}")
                self.errors.append(error)
                return

            # Permit.
            permitStr = RemoveLink(result.get('resource_authority_permit', None),'qld-resource-permit/')


            # Create the permit object.
            if(permitStr is not None):
                permitStr = permitStr.upper()
                permitStr = permitStr.replace(" ", "")
                permitStr = permitStr.replace("PETROLEUMLEASE", "PL")
                permitStr = permitStr.replace("AUTHORITYTOPROSPECT", "ATP")
                permitStr = permitStr.replace("EXPLORATIONPERMITMINERAL", "EPM")

                x = permitStr.find(",")
                if(x > -1):
                    self.success = False
                    myError = errorList[6]
                    error = Error(myError.code,myError.description,myError.consolLog)
                    #print(f"Error {error.code}: {error.consolLog}")
                    self.errors.append(error)
                    return

                permit = Permit.objects.filter(permit_number=permitStr).first()
                if (permit is None):
                    try:
                        permit = Permit.objects.create(permit_number = permitStr)
                    except Exception as e:
                        # Handle Error
                        self.success = False
                        myError = errorList[21]
                        error = Error(myError.code,myError.description,myError.consolLog)
                        error.consolLog = error.consolLog + " Permit: " + permitStr
                        print(f"Error {error.code}: {error.consolLog}")
                        #raise e
                        self.errors.append(error)
                        return
            else:
                permit = None

            # Well name.
            permitStr = result.get('resource_authority_permit', None)
            if(title is not None) and permitStr is not None:
                wellName = GetWellName(title,str(permitStr))
            else: 
                if(title is not None and type=='borehole'):
                    wellName = title.title()
                    permit = Permit.objects.filter(permit_number="No Permit").first()
                    if(permit is None):
                        permit = Permit.objects.create(permit_number="No Permit")
                else:
                    wellName = None
                    print("error getting wellName, Title: " + str(title) + ", Permit: " + str(permitStr))
                    return

            # Well name Alias
            if is_number(wellName):
                alias = result.get('alias', None)
                if(alias is not None):
                    wellName = alias

            # Remove brackets from well name
            wellName = wellName.replace("(","")
            wellName = wellName.replace(")","")

            # Check for question marks
            x = wellName.find("?")
            if(x > -1):
                self.success = False
                myError = errorList[7]
                error = Error(myError.code,myError.description,myError.consolLog)
                #print(f"Error {error.code}: {error.consolLog}")
                self.errors.append(error)
                return

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
                        myError = errorList[10]
                        error = Error(myError.code,myError.description,myError.consolLog)
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
                        myError = errorList[18]
                        error = Error(myError.code,myError.description,myError.consolLog)
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
                        myError = errorList[16]
                        error = Error(myError.code,myError.description,myError.consolLog)
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
                        myError = errorList[17]
                        error = Error(myError.code,myError.description,myError.consolLog)
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
                #myError = errorList[12]
                #error = Error(myError.code,myError.description,myError.consolLog)
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
                    myError = errorList[20]
                    error = Error(myError.code,myError.description,myError.consolLog)
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
                    myError = errorList[11]
                    error = Error(myError.code,myError.description,myError.consolLog)
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
                                myError = errorList[14]
                                error = Error(myError.code,myError.description,myError.consolLog)
                                error.consolLog = error.consolLog + " Well: " + well.well_name + " Document: " + documentName
                                print(f"Error {error.code}: {error.consolLog}")
                                self.errors.append(error)
                        else:
                            # Handle Error.
                            self.success = False
                            myError = errorList[15]
                            error = Error(myError.code,myError.description,myError.consolLog)
                            error.consolLog = error.consolLog + " Well: " + well.well_name + " Document: " + documentName
                            #print(f"Error {error.code}: {error.consolLog}")
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
                                myError = errorList[14]
                                error = Error(myError.code,myError.description,myError.consolLog)
                                print(f"Error {error.code}: {error.consolLog}")
                                self.errors.append(error)
                        else:
                            # Add to report (if duplicate already added without)
                            if(report is not None):
                                try:
                                    document.report = report
                                    document.save()
                                    print("successfully updated report")
                                except:
                                    print("failed to change report")
                            # Handle Error.
                            self.success = False
                            myError = errorList[15]
                            error = Error(myError.code,myError.description,myError.consolLog)
                            error.consolLog = error.consolLog + " Well: " + well.well_name + " Document: " + documentName
                            #print(f"Error {error.code}: {error.consolLog}")
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
                        myResult.permit = RemoveLink(result.get('resource_authority_permit', 'None'),'qld-resource-permit/')
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

                        #if(not myResult.existsInDatabase):
                            #print(result)

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
        mstr = mstr.lower()
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

        # Remove brackets
        wellName = wellName.replace("(","")
        wellName = wellName.replace(")","")

        return wellName.strip()



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False