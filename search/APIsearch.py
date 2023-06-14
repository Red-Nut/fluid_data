from django.utils import timezone
from django.http import JsonResponse

# This module imports.
from . import config_search

# Other module imports.
from data_extraction.functions import wellExists, IsNumber
from data_extraction.models import Company, CompanyNameCorrections, Data, DataType, Document, File, OtherData, Package, Page, Permit, Report, ReportType, State, Well, WellClass, WellStatus, WellPurpose
from data_extraction.responseCodes import Result, GenerateResult, PrintResultLog, searchList as resultList

# Third party imports.
import requests
import json
from datetime import datetime, timedelta
import pytz

def Add(package,state):
    pid=package.gov_id
    
    # Retrieve well government database and save to local database.
    if state == "QLD":
        myRetrive = RetriveQLD(package)
        myRetrive.Retrive()

        # Update the Package
        package.error = None
        package.errorCodes = None
        package.success = myRetrive.success
        if not myRetrive.success:
            errors = ""
            errorCodes = ""
            for error in myRetrive.errors:
                if not error.code == "00000":
                    errors += "E" + error.code + ": " + error.consolLog + " "
                    errorCodes += error.code + ", "
            
            if len(errors) > 2:
                errors = errors[:-1]
            if len(errorCodes) > 2:
                errorCodes = errorCodes[:-2]

            if len(errors) > 999:
                errors = errors[:999]
            if len(errorCodes) > 99:
                errorCodes = errorCodes[:99]

            package.errorCodes = errorCodes
            package.error = errors
            if package.errorCodes == "":
                package.success = True

            #print(f"Package: {package.gov_id} Success: {package.success} Errors: {package.errorCodes}")
        try:
            package.save()
        except Exception as e:
            print(e)
            
        # Create the response object.
        response = {
            'success':myRetrive.success,
            'package':package.gov_id,
            'title':myRetrive.title,
            'well_name':myRetrive.wellName,
            'errors':ResultEncoder().encode(myRetrive.errors)
            }
        
    else: 
        result = GenerateResult(resultList,32)
        PrintResultLog(result)
        errors = []
        errors.append(result)
        response = {
            'success':False,
            'package':pid,
            'title':None,
            'well_name':None,
            'errors':ResultEncoder().encode(errors)
            }

    return response    

def UpdateQLD():
    # Obtains a list of all updated objects in the Queensland government database and attempts to retrieve them all.
    responseList = []

    # Construct the query.
    query = config_search.api + 'recently_changed_packages_activity_list'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # Make the get request and store it in the response object.
    APIresponse = requests.get(query, headers=headers)

    try:
        json_response = json.loads(APIresponse.content.decode("utf-8"))
    except Exception as e:
        if hasattr(e, 'message'):
            # Handle Error
            result = GenerateResult(resultList,4)
            result.consolLog = result.consolLog + ". Query: " + query + " Message: " + e.message
            PrintResultLog(result)
            responseList.append(result)
            return responseList
        else:
            # Handle Error
            result = GenerateResult(resultList,4)
            result.consolLog = result.consolLog + ". Query: " + query
            PrintResultLog(result)
            print(e)
            responseList.append(result)
            return responseList

    print("********** JSON RESPONSE ***********")    
    print(json_response)
    print("************************************")  

    # Check for API success.
    success = json_response["success"]
    if(success != True):
        # Handle Error
        result = GenerateResult(resultList,1)
        result.consolLog = result.consolLog + ". Query: " + query
        PrintResultLog(result)
        responseList.append(result)
        return responseList
    else:
        # Iterate through each package.
        packages = json_response['result']
        count = 0
        for packageObject in packages:
            objectId = packageObject['object_id']
            # Construct the query.
            query = config_search.api + "package_show?id=" + objectId
            # Make the get request and store it in the response object.
            APIresponse = requests.get(query, headers=headers)

            chk = False
            try:
                json_response2 = json.loads(APIresponse.content.decode("utf-8"))
                success2 = json_response2["success"]
                if(success2 != True):
                    # Handle Error
                    result = GenerateResult(resultList,1)
                    result.consolLog = result.consolLog + ". Query: " + query
                    PrintResultLog(result)
                    responseList.append(result)

                else:
                    # Iterate through each package.
                    pid = json_response2['result']["name"]
                    chk = True

            except Exception as e:
                if hasattr(e, 'message'):
                    # Handle Error
                    result = GenerateResult(resultList,4)
                    result.consolLog = result.consolLog + ". Query: " + query + " Message: " + e.message
                    PrintResultLog(result)
                    responseList.append(result)
                else:
                    # Handle Error
                    result = GenerateResult(resultList,4)
                    result.consolLog = result.consolLog + ". Query: " + query
                    PrintResultLog(result)
                    print(e)
                    responseList.append(result)

            if chk:
                package = Package.objects.filter(gov_id=pid).first()
                if package is None:
                    print(f"New Package: {pid}")
                    check = False
                    try:
                        package = Package.objects.create(gov_id=pid)
                        check=True
                    except Exception as e:
                        result = GenerateResult(resultList,36)
                        PrintResultLog(result)
                    
                    if check:
                        response = Add(package,"QLD")
                        responseList.append(response)
                        
                        count += 1
                else:
                    package.error = None
                    package.errorCodes = None
                
                    response = Add(package,"QLD")
                    responseList.append(response)

                    count += 1

            

            if count > 400000:
                break

        return responseList


def RetreiveAllQLD():
    recheckDays = 30

    # Obtains a list of all objects in the Queensland government database and attempts to retrieve them all.
    responseList = []

    state = State.objects.filter(name_short="QLD").first()
    # Create the Queensland state object on database initialisation.
    if(state is None):
        state = State.objects.create(name_long = "Queensland", name_short="QLD")

    # Construct the query.
    query = config_search.api + 'package_list'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # Make the get request and store it in the response object.
    APIresponse = requests.get(query, headers=headers)

    try:
        json_response = json.loads(APIresponse.content.decode("utf-8"))
    except Exception as e:
        if hasattr(e, 'message'):
            # Handle Error
            result = GenerateResult(resultList,4)
            result.consolLog = result.consolLog + ". Query: " + query + " Message: " + e.message
            PrintResultLog(result)
            responseList.append(result)
            return responseList
        else:
            # Handle Error
            result = GenerateResult(resultList,4)
            result.consolLog = result.consolLog + ". Query: " + query
            PrintResultLog(result)
            print(e)
            responseList.append(result)
            return responseList
            
    # Check for API success.
    success = json_response["success"]
    if(success != True):
        # Handle Error
        result = GenerateResult(resultList,1)
        result.consolLog = result.consolLog + ". Query: " + query
        PrintResultLog(result)
        responseList.append(result)
        return responseList
    else:
        # Iterate through each package.
        packages = json_response['result']
        count = 0
        for pid in packages:
            package = Package.objects.filter(gov_id=pid).first()
            if package is None:
                #print(f"Package: {pid}")
                check = False
                try:
                    package = Package.objects.create(gov_id=pid)
                    check=True
                except Exception as e:
                    result = GenerateResult(resultList,36)
                    PrintResultLog(result)
                
                if check:
                    response = Add(package,"QLD")
                    responseList.append(response)
                    
                    count += 1
            else:
                package.error = None
                package.errorCodes = None
                #USE_TZ=True
                #if (package.success == False or (package.checked + timedelta(days=recheckDays))  < timezone.now()):
                if (package.checked + timedelta(days=recheckDays))  < timezone.now():
                    #print(f"Package: {pid}")
                    response = Add(package,"QLD")
                    responseList.append(response)

                    count += 1

            

            if count > 400000:
                break

        return responseList

def UpdateId(wellName, gov_id):
    well = Well.objects.filter(well_name=wellName).first()
    well.gov_id=gov_id

    # Save the updated records
    try:
        well.save()
        result = GenerateResult(resultList,0)
        return result
    except Exception as e:
        result = GenerateResult(resultList,20)
        if hasattr(e, 'message'):
            #print(e.message)
            result.consolLog = result.consolLog + e.message
        else:
            print(e)
        PrintResultLog(result)
        return result

def UpdateValues(wellName, company, status, wellClass, purpose, permit, lat, long, rigRelease, package):
    well = Well.objects.filter(well_name=wellName).first()
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
    if(package is not None):
        well.package = package

    # Save the updated records
    try:
        well.save()
        result = GenerateResult(resultList,0)
        return result
    except Exception as e:
        result = GenerateResult(resultList,20)
        if hasattr(e, 'message'):
            #print(e.message)
            result.consolLog = result.consolLog + e.message
        else:
            print(e)
        PrintResultLog(result)
        return result

def UpdateNullValues(wellName, gov_id, company, status, wellClass, purpose, permit, lat, long, rigRelease, package):
    well = Well.objects.filter(well_name=wellName).first()

    # Update gov id for boreholes
    if(gov_id is not None):
        well.gov_id = gov_id

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
    if(well.package is None and package is not None):
        well.package = package

    # Save the updated records
    try:
        well.save()
        result = GenerateResult(resultList,0)
        return result
    except Exception as e:
        result = GenerateResult(resultList,20)
        if hasattr(e, 'message'):
            #print(e.message)
            result.consolLog = result.consolLog + e.message
        else:
            print(e)
        PrintResultLog(result)
        return result

def CreateWell(gov_id, wellName, state, company, status, wellClass, purpose, permit, lat, long, rigRelease, package):
    try:
        well = Well.objects.create(
            gov_id = gov_id,
            well_name = wellName,
            owner = company,
            state = state,
            status = status,
            well_class = wellClass,
            purpose = purpose,
            permit = permit,
            latitude = lat,
            longitude = long,
            rig_release = rigRelease,
            package = package
        )
        result = GenerateResult(resultList,0)
        return result
    except Exception as e:
        result = GenerateResult(resultList,11)
        if hasattr(e, 'message'):
            #print(e.message)
            result.consolLog = result.consolLog + e.message
        else:
            print(e)
        # Handle Error
        PrintResultLog(result)
        return result

def ProcessWellName(title,type, permitStr, alias):
    if(title is not None) and permitStr is not None:
        wellName = title

        # Remove permit.
        if(permitStr + "," in wellName):
            x = wellName.find(permitStr + ",")
            wellName = wellName[:x] + wellName[x+len(permitStr)+1:]
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

        wellName = wellName.strip()
    else:
        if(title is not None and type=='borehole'):
            # Assign the "No Permit" permit
            permit = Permit.objects.filter(permit_number="No Permit").first()
            if(permit is None):
                permit = Permit.objects.create(permit_number="No Permit")

            wellName = title.title()
        else:
            wellName = None
            print("error getting wellName, Title: " + str(title) + ", Permit: " + str(permitStr))
                # Handle Error
            result = GenerateResult(resultList,8)
            result.consolLog = result.consolLog + ". Error processing Well Name. Title: " + str(title) + " Permit: " + str(permitStr)
            PrintResultLog(result)
            return result
            
    # Remove brackets from well name
    wellName = wellName.replace("(","")
    wellName = wellName.replace(")","")

    # Check for question marks
    x = wellName.find("?")
    if(x > -1):
        result = GenerateResult(resultList,8)
        consoleLog = result.consolLog + ". Found ? in Well Name: "
        if wellName is not None:
            consoleLog += wellName
        else:
            consoleLog += "None"
        result.consolLog = consoleLog

        PrintResultLog(result)

        return result

    if IsNumber(wellName):
        if(alias is not None):
            wellName = alias

    result = GenerateResult(resultList,0)
    result.wellName=wellName
    return result

def RemoveLink(mstr, subFolder):
    if(mstr is not None):
        tstr = mstr.lower()
        x = tstr.find("http://linked.data.gov.au/def/" + subFolder)
        if(x > -1):
            mstr = tstr[x+30 + len(subFolder):]
    
    return mstr


class RetriveQLD:
    def __init__(self, package):
        self.id = package.gov_id
        self.package = package
        self.wellName = ""
        self.title = ""
        self.state = State.objects.filter(name_short="QLD").first()
        self.result = None
        self.resources = None
        self.errors = []
        self.success = None

    def Retrive(self):
        # Retrives the package with the given id. 

        # Construct the query.
        query = config_search.api + 'package_show?'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        
        # Make the get request and store it in the response object.
        try:
            APIresponse = requests.get(query, headers=headers,params=dict(id=self.id))
        except Exception as e:
            if hasattr(e, 'message'):
                # Handle Error
                result = GenerateResult(resultList,31)
                result.consolLog = result.consolLog + " Package: " + self.id + " Message: " + e.message
                PrintResultLog(result)
                self.errors.append(result)
                return
            else:
                # Handle Error
                result = GenerateResult(resultList,31)
                result.consolLog = result.consolLog + " Package: " + self.id
                PrintResultLog(result)
                print(e)
                self.errors.append(result)
                return
        try:
            json_response = json.loads(APIresponse.content.decode("utf-8"))
        except Exception as e:
            if hasattr(e, 'message'):
                # Handle Error
                result = GenerateResult(resultList,4)
                result.consolLog = result.consolLog + ". Query: " + query + " Message: " + e.message
                PrintResultLog(result)
                self.errors.append(result)
                return
            else:
                # Handle Error
                result = GenerateResult(resultList,4)
                result.consolLog = result.consolLog + ". Query: " + query
                PrintResultLog(result)
                print(e)
                self.errors.append(result)
                return

        # Check for API success.
        success = json_response["success"]
        if(success != True):
            # Handle Error
            result = GenerateResult(resultList,1)
            result.consolLog = result.consolLog + ". Query: " + query
            PrintResultLog(result)
            self.errors.append(result)
            return
        else:
            self.result = json_response['result']
            self.resources = self.result['resources']

            reportType = self.CheckReportType()

            if reportType == "WellReport":
                # Process well metadata.
                result = self.ProcessWellResult()            
                if(result.code != "00000"):
                    if result.code == "00015":
                        self.success = result.success
                    else:
                        self.success = False
                    self.errors.append(result)
                    return
                
                result = self.ProcessResources() 
                if(result.code != "00000"):
                    if result.code == "00015":
                        self.success = result.success
                    else:
                        self.success = False
                    self.errors.append(result)
                    return

            if reportType == "OtherReport":
                result = self.ProcessOtherReport()
                if(result.code != "00000"):
                    if result.code == "00015":
                        self.success = result.success
                    else:
                        self.success = False
                    self.errors.append(result)
                    return

                result = self.ProcessResources() 
                if(result.code != "00000"):
                    if result.code == "00015":
                        self.success = result.success
                    else:
                        self.success = False
                    self.errors.append(result)
                    return

            if reportType == "OtherData":
                #result = self.ProcessOtherData()
                #if(result.code != "00000"):
                #    self.success = False
                #    self.errors.append(result)
                #    return
                    
                result = self.ProcessResources() 
                if(result.code != "00000"):
                    if result.code == "00015":
                        self.success = result.success
                    else:
                        self.success = False
                    self.errors.append(result)
                    return
            

            # Confirm the success or failure of adding the well.
            #print(self.success)
            if(self.success is None):
                self.success = True

            return

    def CheckReportType(self):
        dataTypeStr = self.ProcessType()
        if dataTypeStr == "borehole":
            return "WellReport"

        reportTypeStr = RemoveLink(self.result.get('georesource_report_type', None),'georesource-report/')

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
                
                return "OtherReport"
            else:
                return "WellReport"
        else:
            return "OtherData"


    def ProcessWellResult(self):
        # Check Valid Permit
        result = self.CheckValidPermit()
        if(result.code != "00000" and result.code != "10007"):
            self.success = False
            self.errors.append(result)
            return result

        # Get variables.
        title = self.ProcessTitle()
        alias = self.result.get('alias', None)
        type = self.ProcessType()
        #reportType = self.ProcessReportType()
        govId = self.ProcessGovId()
        permitStr = self.result.get('resource_authority_permit', None)
        permit = self.ProcessPermit()

        # Data Checks
        if title is None or type is None or govId is None:
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,8)
            return result

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
            result = GenerateResult(resultList,5)
            result.consolLog = result.consolLog + ". Type: " + type
            result.description = result.description + ". Type: " + type
            self.errors.append(result)
            return result

        # Get variables.
        result = ProcessWellName(title, type, permitStr,alias)
        if result.code!="00000":
            return result
        wellName = result.wellName
        self.wellName = wellName
        operator = self.ProcessOperator()
        status = self.ProcessStatus()
        wellClass = self.ProcessClass()
        purpose = self.ProcessPurpose()
        GeoJSONextent = self.ProcessGEOData() # Geodata (Not used yet).
        coords = self.ProcessLatLong(GeoJSONextent)
        rigRelease = self.ProcessRigRelease()
        modified = self.ProcessModified()

        # Data Checks
        if wellName is None:
            # Handle Error
            result = GenerateResult(resultList,9)
            consoleLog = result.consolLog
            consoleLog += f" Title: {title} Permit: {permitStr}"
            result.consolLog = consoleLog
            PrintResultLog(result)
            return result

        # Finalise
        if (wellExists(wellName)):
            well = Well.objects.filter(well_name=wellName).first()
            if(type == "borehole"):
                # Update id if object is the borehole
                result = UpdateNullValues(wellName, govId, operator, status, wellClass, purpose, permit, coords["lat"], coords["long"], rigRelease, self.package)
                return result

            if self.package.modified is not None:
                if(modified > self.package.modified):
                    # Update all values.
                    result = UpdateValues(wellName, operator, status, wellClass, purpose, permit, coords["lat"], coords["long"], rigRelease, self.package)
                    return result
                else:
                    # Update any null values.
                    result = UpdateNullValues(wellName, None, operator, status, wellClass, purpose, permit, coords["lat"], coords["long"], rigRelease, self.package)
                    return result
            else:
                # Update all values.
                result = UpdateValues(wellName, operator, status, wellClass, purpose, permit, coords["lat"], coords["long"], rigRelease, self.package)
                return result
        else:
            # Create new well.
            result = CreateWell(govId, wellName, self.state, operator, status, wellClass, purpose, permit, coords["lat"], coords["long"], rigRelease, self.package)
            return result

    def CheckValidPermit(self):
        # Permit.
        permitStr = RemoveLink(self.result.get('resource_authority_permit', None),'qld-resource-permit/')
        # Create the permit object.
        if permitStr is not None:
            x = permitStr.find(",")
            if(x > -1):
                result = GenerateResult(resultList,26)
                result.consolLog = result.consolLog + ". Permit: " + permitStr
                return result
            else:
                result = GenerateResult(resultList,0)
                return result 
        else:
            result = GenerateResult(resultList,7)
            PrintResultLog(result)
            return result            


    def ProcessOtherReport(self):
        self.wellName = None

        reportType = self.ProcessReportType()
        if (reportType is None):
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,28)
            PrintResultLog(result)
            self.errors.append(result)
        
        # Get variables.
        title = self.ProcessTitle()
        url = self.result.get('url', None)
        govId = self.ProcessGovId()
        creator = self.result.get('creator', None)

        metadata_modified_str = self.result.get('metadata_modified', None)
        metadata_modified = config_search.ConvertQLDDateTime(metadata_modified_str)

        metadata_created_str = self.result.get('metadata_created', None)
        metadata_created = config_search.ConvertQLDDateTime(metadata_created_str)

        dataset_completion_date_str = self.result.get('dataset_completion_date', None)
        dataset_completion_date = config_search.ConvertQLDDate(dataset_completion_date_str)

        open_file_date_str = self.result.get('open_file_date', None)
        open_file_date = config_search.ConvertQLDDate(open_file_date_str)

        # Data Checks
        if title is None or govId is None:
            result = GenerateResult(resultList,8)
            return result

        try:
            otherReport = Report.objects.create( 
                    url=url,
                    gov_id = govId,
                    gov_report_name=title,
                    gov_creator=creator,
                    gov_created=metadata_modified,
                    gov_modified=metadata_created,
                    gov_dataset_completion_date=dataset_completion_date,
                    gov_open_file_date=open_file_date,
                    report_name=title,
                    report_type = reportType,
                )
            result = GenerateResult(resultList,0)
            return result
        except Exception as e:
            result = GenerateResult(resultList,29)
            if hasattr(e, 'message'):
                #print(e.message)
                result.consolLog = result.consolLog + e.message
            else:
                print(e)
            # Handle Error
            PrintResultLog(result)
            return result


    def ProcessOtherReportResources(self, otherReport):
        for resource in self.resources:
            # Check if resource is active.
            if (resource['state'] == "active"):

                # Document Name.
                documentName = resource['name']
                
                # URL.
                url = resource['url']

                # Check if document exists.
                document = Document.objects.filter(document_name=documentName).first()
                if(document is None):
                    try:
                        document = Document.objects.create(
                            document_name = documentName,
                            well=well,
                            url = url,
                            report=report
                        )
                    except:
                        # Handle Error
                        self.success = False
                        result = GenerateResult(resultList,14)
                        result.consolLog = result.consolLog + " Well: " + well.well_name + " Document: " + documentName
                        PrintResultLog(result)
                        self.errors.append(result)
                        return result
                else:
                    # Add to report (if duplicate already added without)
                    if(otherReport is not None):
                        try:
                            document.other_report = otherReport
                            document.save()
                        except Exception as e:
                            result = GenerateResult(resultList,30)
                            if hasattr(e, 'message'):
                                #print(e.message)
                                result.consolLog = result.consolLog + e.message
                            else:
                                print(e)
                            PrintResultLog(result)
                            return result
                    
                    # Handle Error
                    self.success = False
                    result = GenerateResult(resultList,15)
                    result.consolLog = result.consolLog + " Well: " + well.well_name + " Document: " + documentName
                    PrintResultLog(result)
                    self.errors.append(result)
                    return result
    
    def ProcessOtherData(self):
        self.wellName = None

        dataTypeStr = self.ProcessType()

        if (dataTypeStr is None):
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,25)
            PrintResultLog(result)
            self.errors.append(result)

        dataType = DataType.objects.filter(type_name=dataTypeStr).first()
        if dataType == None:
            dataType = DataType.objects.create(type_name=dataTypeStr)
        
        # Get variables.
        title = self.ProcessTitle()
        url = self.result.get('url', None)
        govId = self.ProcessGovId()
        creator = self.result.get('creator', None)

        metadata_modified_str = self.result.get('metadata_modified', None)
        metadata_modified = config_search.ConvertQLDDateTime(metadata_modified_str)

        metadata_created_str = self.result.get('metadata_created', None)
        metadata_created = config_search.ConvertQLDDateTime(metadata_created_str)

        dataset_completion_date_str = self.result.get('dataset_completion_date', None)
        dataset_completion_date = config_search.ConvertQLDDate(dataset_completion_date_str)

        open_file_date_str = self.result.get('open_file_date', None)
        open_file_date = config_search.ConvertQLDDate(open_file_date_str)

        # Data Checks
        if title is None or govId is None:
            result = GenerateResult(resultList,8)
            return result

        try:
            otherData = OtherData.objects.create( 
                    url=url,
                    gov_id = govId,
                    gov_report_name=title,
                    gov_creator=creator,
                    gov_created=metadata_modified,
                    gov_modified=metadata_created,
                    gov_dataset_completion_date=dataset_completion_date,
                    gov_open_file_date=open_file_date,
                    data_name=title,
                    data_type = dataType,
                )
            result = GenerateResult(resultList,0)
            return result
        except Exception as e:
            result = GenerateResult(resultList,29)
            if hasattr(e, 'message'):
                #print(e.message)
                result.consolLog = result.consolLog + e.message
            else:
                print(e)
            # Handle Error
            PrintResultLog(result)
            return result

        return


    def ProcessTitle(self):
        title = self.result.get('title', None)
        self.title = title

        if title is None:
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,8)
            result.consolLog = result.consolLog + ". Title: None"
            PrintResultLog(result)
            self.errors.append(result)

        return title

    def ProcessType(self):
        type = self.result.get('type', None)

        if type is None:
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,8)
            result.consolLog = result.consolLog + ". Type: None"
            PrintResultLog(result)
            self.errors.append(result)

        return type

    def ProcessReportType(self):
        reportTypeStr = RemoveLink(self.result.get('georesource_report_type', None),'georesource-report/')

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
                    result = GenerateResult(resultList,19)
                    PrintResultLog(result)
                    self.errors.append(result)
                    return

            return reportType
        else: 
            return None

    def ProcessGovId(self):
        gov_id = self.result.get('name', None)
        if(gov_id is None):
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,3)
            PrintResultLog(result)
            self.errors.append(result)

        return gov_id

    def ProcessPermit(self):
        result = self.CheckValidPermit()
        if(result.code == "10007"):
            return None
        elif(result.code != "00000" and result.code != "10007"):
            self.success = False
            self.errors.append(result)
            return result
        else:
            # Permit.
            permitStr = RemoveLink(self.result.get('resource_authority_permit', None),'qld-resource-permit/')
            # Create the permit object.
            if(permitStr is not None):
                permitStr = permitStr.upper()
                permitStr = permitStr.replace(" ", "")
                permitStr = permitStr.replace("PETROLEUMLEASE", "PL")
                permitStr = permitStr.replace("AUTHORITYTOPROSPECT", "ATP")
                permitStr = permitStr.replace("EXPLORATIONPERMITMINERAL", "EPM")

                
                permit = Permit.objects.filter(permit_number=permitStr).first()
                if (permit is None):
                    try:
                        permit = Permit.objects.create(permit_number = permitStr)
                    except Exception as e:
                        # Handle Error
                        self.success = False
                        result = GenerateResult(resultList,21)
                        result.consolLog = result.consolLog + " Permit: " + permitStr
                        PrintResultLog(result)
                        self.errors.append(result)
                        return

                return permit
            else:
                return None                

    def ProcessOperator(self):
        operator = self.result.get('owner', 'None').title()
        if(operator == 'None'):
            operator = self.result.get('operator', 'None').title()

        if(operator == 'None'):
            return None

        # Operator corrections
        correction = CompanyNameCorrections.objects.filter(alternateName=operator).first()
        if(correction is not None):
            company = Company.objects.filter(company_name=correction.correctName).first()
            if (company is not None):
                operator = company.company_name

        # Create the company object.
        company = Company.objects.filter(company_name=operator).first()
        if (company is None):
            try:
                company = Company.objects.create(company_name = operator)
            except:
                # Handle Error
                self.success = False
                result = GenerateResult(resultList,10)
                result.consolLog = result.consolLog + ". Company: " + operator
                PrintResultLog(result)
                self.errors.append(result)
                return None
        
        return company

    def ProcessStatus(self):
        statusStr = self.result.get('state', None).title()

        # Create the well status object.
        if(statusStr is not None):
            status = WellStatus.objects.filter(status_name=statusStr).first()
            if (status is None):
                try:
                    status = WellStatus.objects.create(status_name = statusStr)
                except:
                    # Handle Error
                    self.success = False
                    result = GenerateResult(resultList,18)
                    result.consolLog = result.consolLog + ". State: " + statusStr
                    PrintResultLog(result)
                    self.errors.append(result)
                    return None
            return status
        else:
            return None

    def ProcessClass(self):
        # Well Class.
        wellClassStr = RemoveLink(self.result.get('borehole_class', None),"resource-project-lifecycle/")
        
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
                    result = GenerateResult(resultList,16)
                    result.consolLog = result.consolLog + ". Class: " + wellClassStr
                    PrintResultLog(result)
                    self.errors.append(result)
                    return None
            
            return wellClass
        else: 
            return None

    def ProcessPurpose(self):
        # Well Class.
        wellPurposeStr = RemoveLink(self.result.get('borehole_purpose', None),"borehole-purpose/")
        
        # Create the well class object.
        if(wellPurposeStr is not None):
            wellPurposeStr = wellPurposeStr.replace("-"," ").title()
            purpose = WellPurpose.objects.filter(purpose_name=wellPurposeStr).first()
            if (purpose is None):
                try:
                    wellClass = WellClass.objects.create(class_name = wellPurposeStr)
                except:
                    # Handle Error
                    self.success = False
                    result = GenerateResult(resultList,17)
                    result.consolLog = result.consolLog + ". Purpose: " + wellPurposeStr
                    PrintResultLog(result)
                    self.errors.append(result)
                    return None
            
            return purpose
        else: 
            return None

    def ProcessGEOData(self):  
        GeoJSONextent = self.result.get('GeoJSONextent', None)
        return GeoJSONextent

    def ProcessLatLong(self, GeoJSONextent):
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

        coords = {}
        coords["lat"] = lat
        coords["long"] = long

        return coords

    def ProcessRigRelease(self):
        # Rig Release.
        rigReleaseStr = self.result.get('rig_release_date', None)
        rigRelease = config_search.ConvertQLDDate(rigReleaseStr)
        return rigRelease
        
    def ProcessModified(self):
        # Modified.
        modifiedStr = self.result.get('metadata_modified', None)
        modified = config_search.ConvertQLDDateTime(modifiedStr)
        return modified

    def ProcessResources(self):
        # Process well resource data
        if self.wellName != None:
            well = Well.objects.filter(well_name=self.wellName).first()
            wellName = self.wellName
        else: 
            well = None
            wellName = "None"

        reportTypeCheck = self.CheckReportType()

        type = self.ProcessType()
        govId = self.ProcessGovId()
        reportType = self.ProcessReportType()
        title = self.ProcessTitle()

        # Report data
        creator = self.result.get('creator', None)

        metadata_modified_str = self.result.get('metadata_modified', None)
        metadata_modified = config_search.ConvertQLDDateTime(metadata_modified_str)

        metadata_created_str = self.result.get('metadata_created', None)
        metadata_created = config_search.ConvertQLDDateTime(metadata_created_str)

        dataset_completion_date_str = self.result.get('dataset_completion_date', None)
        dataset_completion_date = config_search.ConvertQLDDate(dataset_completion_date_str)

        open_file_date_str = self.result.get('open_file_date', None)
        open_file_date = config_search.ConvertQLDDate(open_file_date_str)

        urlType = self.result.get('type', None)
        if(urlType is not None and id is not None):
            reportUrl = config_search.urlBase + '/' + urlType + '/' + govId
        else:
            reportUrl = None
        
        if (reportTypeCheck == "WellReport" or reportTypeCheck == "OtherReport"):
            # Wells and Well Reports
            if(reportTypeCheck == "WellReport"):
                if (type == "report" and reportType is not None):
                    # Create the report object.
                    if(well is not None and reportType.type_name == "Well Completion Report"):
                        reportTitle = "Well Completion Report: " + well.well_name
                    else:
                        reportTitle = title

                    # Check if report exists.
                    report = Report.objects.filter(gov_id=govId).first()
                    if(report is None):
                        report = Report.objects.create(
                            well=well, 
                            url=reportUrl,
                            gov_id = govId,
                            gov_report_name=title,
                            gov_creator=creator,
                            gov_created=metadata_modified,
                            gov_modified=metadata_created,
                            gov_dataset_completion_date=dataset_completion_date,
                            gov_open_file_date=open_file_date,
                            report_name=reportTitle,
                            report_type = reportType,
                        )
                else:
                    report = None

            # Other Reports
            elif (reportTypeCheck == "OtherReport"):
                # Create the report object.
                    reportTitle = title

                    # Check if report exists.
                    report = Report.objects.filter(gov_id=govId).first()
                    if(report is None):
                        report = Report.objects.create(
                            well=well, 
                            url=reportUrl,
                            gov_id = govId,
                            gov_report_name=title,
                            gov_creator=creator,
                            gov_created=metadata_modified,
                            gov_modified=metadata_created,
                            gov_dataset_completion_date=dataset_completion_date,
                            gov_open_file_date=open_file_date,
                            report_name=reportTitle,
                            report_type = reportType,
                        )

            for resource in self.resources:
                # Check if resource is active.
                if (resource['state'] == "active"):

                    # Document Name.
                    documentName = resource['name']
                    
                    # URL.
                    url = resource['url']

                    # Check if document exists.
                    if well is not None:
                        document = Document.objects.filter(well=well,document_name=documentName).first()
                    else:
                        document = Document.objects.filter(report=report,document_name=documentName).first()
                    if(document is None):
                        try:
                            document = Document.objects.create(
                                document_name = documentName,
                                well=well,
                                url = url,
                                report=report
                            )
                        except:
                            # Handle Error
                            self.success = False
                            result = GenerateResult(resultList,14)
                            result.consolLog = result.consolLog + " Well: " + str(well) + " Document: " + documentName
                            PrintResultLog(result)
                            self.errors.append(result)
                            return result
                    else:
                        # Add to report (if duplicate already added without)
                        if(report is not None):
                            try:
                                document.report = report
                                document.save()
                            except Exception as e:
                                result = GenerateResult(resultList,22)
                                if hasattr(e, 'message'):
                                    #print(e.message)
                                    result.consolLog = result.consolLog + e.message
                                else:
                                    print(e)
                                PrintResultLog(result)
                                return result
                        
                        # Handle Error
                        self.success = True
                        result = GenerateResult(resultList,0)
                        result.consolLog = result.consolLog + " Duplicate Document. Well: " + wellName + " Document: " + documentName
                        PrintResultLog(result)
                        self.errors.append(result)
                        return result
            
            result = GenerateResult(resultList,0)
            return result    

        # Other Data
        elif (reportTypeCheck == "OtherData"):
            self.wellName = None
            wellName = "None"

            dataTypeStr = type

            if (dataTypeStr is None):
                # Handle Error
                self.success = False
                result = GenerateResult(resultList,25)
                PrintResultLog(result)
                self.errors.append(result)

            dataType = DataType.objects.filter(type_name=dataTypeStr).first()
            if dataType == None:
                dataType = DataType.objects.create(type_name=dataTypeStr)
            
            for resource in self.resources:
                # Get variables.
                documentName = resource['name']
                url = self.result.get('url', None)

                # Data Checks
                if title is None or govId is None:
                    result = GenerateResult(resultList,8)
                    return result
                # Check if document exists.
                otherData = OtherData.objects.filter(package=self.package,data_name=documentName).first()
                if(otherData is None):
                    try:
                        otherData = OtherData.objects.create( 
                                url=url,
                                gov_id = govId,
                                gov_report_name=title,
                                gov_creator=creator,
                                gov_created=metadata_modified,
                                gov_modified=metadata_created,
                                gov_dataset_completion_date=dataset_completion_date,
                                gov_open_file_date=open_file_date,
                                data_name=title,
                                data_type = dataType,
                                package=self.package
                            )
                        result = GenerateResult(resultList,0)
                        return result
                    except Exception as e:
                        result = GenerateResult(resultList,35)
                        if hasattr(e, 'message'):
                            #print(e.message)
                            result.consolLog = result.consolLog + e.message
                        else:
                            print(e)
                        # Handle Error
                        PrintResultLog(result)
                        return result

                else:
                    # Handle Error
                    self.success = False
                    result = GenerateResult(resultList,15)
                    result.consolLog = result.consolLog + " Package: " + self.package.gov_id + " Data: " + documentName
                    PrintResultLog(result)
                    self.errors.append(result)
                    return result
            
        result = GenerateResult(resultList,34)
        return result    
          


                                        
                 


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
            result = GenerateResult(resultList,4)
            if hasattr(e, 'message'):
                #print(e.message)
                result.consolLog = result.consolLog + e.message
            else:
                print(e)
            # Handle Error
            PrintResultLog(result)
            self.errors.append(result)
            return result

        success = json_response["success"]

        if(success != True):
            # Handle Error
            self.success = False
            result = GenerateResult(resultList,1)
            PrintResultLog(result)
            self.errors.append(result)
            return
        else:
            # Cycle through search results.
            for result in json_response['result']['results']:
                myID = result.get('id', 'None')
                if(myID != 'None'):
                    myResult = DataPackage(myID)
                    
                    # Get the number of resources.
                    myResult.num_resources = int(result.get('num_resources', 0))
                    # Get the report type.
                    georesource_report_type = RemoveLink(result.get('georesource_report_type', 'None'),'georesource-report/')

                    #Perform checks on resouce count (results with attachments only) and report type (WCRs only).
                    if((myResult.num_resources > 0 or self.attachmentsOnly == False) and \
                        (georesource_report_type == 'well-completion-report' or self.WCRonly == False)):

                        # Get general data.
                        myResult.name = result.get('name', 'None')
                        myResult.alias = result.get('alias', None)
                        myResult.title = result.get('title', 'None')
                        myResult.type = georesource_report_type.replace('-'," ").title()
                        myResult.owner = result.get('owner', 'None').title()
                        myResult.permit = RemoveLink(result.get('resource_authority_permit', 'None'),'qld-resource-permit/')
                        myResult.GeoJSONextent = result.get('GeoJSONextent', 'None')
                        wellNameResult = ProcessWellName(myResult.title,myResult.type, myResult.permit, myResult.alias)
                        if wellNameResult.code == "00000":
                            myResult.wellName = wellNameResult.wellName
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

class DataPackage:
    def __init__(self,id):
        self.id = id
        self.num_resources = 0
        self.resources = []

    def __repr__(self):
        str = "Title: {}\n" 
        str =str.format( self.title)
        return str

class ResultEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

def xstr(s):
    if s is None:
        return ''
    return str(s)





