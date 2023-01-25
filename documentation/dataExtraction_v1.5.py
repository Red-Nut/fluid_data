#*********************** IMPORTS ******************************
import io
import os
import sys
import glob
import math
import csv
from termcolor import colored #pip install termcolor

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types #pip install google.cloud.vision
#===============================================================
os.system('color')

print(colored("********* BEGIN RUN ********* \r\n",'green'))

#*********************** CONFIGURATION *************************
#CSV Output
    #File name
outputFileName = "output.csv"

    #Title Row (needs to be consistent with layouts)
#data = [["Filename","Page","Well","Sample","Top (m)","Bottom (m)","Relative Density (g/cc)","Moisture (%)","Ash (%)","Q1 (Raw)","Q2 (Raw)","Q3 (Raw)","Q1+Q2+Q3 (Raw)","Q1 (daf)","Q2 (daf)","Q3 (daf)","Q1+Q2+Q3 (daf)"]]

baseFolder = "Y:\\DATA\\QLD\\WCR\\"
wellname = "CLEMATIS_CREEK_1"
baseFolder += wellname
#===============================================================

#*********************** CREDENTIALS **************************
credential_path = os.getcwd() + "\\Data Extraction-42569ca311b6.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

print("********* Authentification Complete ********* \r\n")
#===============================================================

#*********************** MASTER CODE **************************
#varialbes
data = []

def main():
    #get all files and folders in the well folder
    wellFolderContents = os.scandir(baseFolder)
    for entry in wellFolderContents :

        #check each file (ignore folders)
        if entry.is_file():
            fname, ext = os.path.splitext(entry.name)

            #check if file is tif or pdf (ignore other files)
            if(ext==".tiff" or ext==".tif" or ext==".pdf"):
                print(" ") #spacer
                #ignore certain files
                if ("casing and complet" in fname.lower()):                     #CASING AND COMPLETE
                    print(colored("Skipping Casing and Completion Appendix: " + entry.name,'yellow'))
                elif ("core descript" in fname.lower()):                        #CORE
                    print(colored("Skipping Core Description Appendix: " + entry.name,'yellow'))
                elif ("cuttin" in fname.lower()):                               #CUTTINGS
                    print(colored("Skipping Core Description Appendix: " + entry.name,'yellow'))
                elif ("depth vs. temp" in fname.lower()):                       #DEPTH VS TEMP
                    print(colored("Skipping Depth vs Temperature Appendix: " + entry.name,'yellow'))
                elif ("drilling" in fname.lower()):                             #DRILLING
                    print(colored("Skipping Drilling Appendix: " + entry.name,'yellow'))
                elif ("fluid record" in fname.lower()):                         #FLUID RECORD
                    print(colored("Skipping Drilling Fluid Record Appendix: " + entry.name,'yellow'))
                elif ("litholog" in fname.lower()):                             #LITHOLOGY
                    print(colored("Skipping Lithology Appendix: " + entry.name,'yellow'))
                elif ("oil_f" in fname.lower()):                                #OIL FINGERPRINT
                    print(colored("Skipping Oil Fingerprint Appendix: " + entry.name,'yellow'))
                elif ("quantitative log interpretation" in fname.lower()):      #QUANTATIVE LOG INTERPRETATION
                    print(colored("Skipping Quantatiative Log interpretation Appendix: " + entry.name,'yellow'))
                elif ("source rock" in fname.lower()):                          #SOURCE ROCK
                    print(colored("Skipping Source Rock Analysis Appendix: " + entry.name,'yellow'))
                                                                                #TIME DEPTH CURVES
                elif ("time-depth" in fname.lower() or "time- depth" in fname.lower() or "time - depth" in fname.lower() or "time -depth" in fname.lower()):
                    print(colored("Skipping Time-Depth Curve: " + entry.name,'yellow'))
                elif ("velocity" in fname.lower()):                             #VELOCITY
                    print(colored("Skipping Velocity Appendix: " + entry.name,'yellow'))
                                                                                #WATER ANALYSIS
                elif ("water analysis" in fname.lower() or "water anaylsis" in fname.lower() or "water_a" in fname.lower()):
                    print(colored("Skipping Water Analysis Appendix: " + entry.name,'yellow'))
                elif ("well_loc" in fname.lower() or "location" in fname.lower()):  #WELL LOCATION
                    print(colored("Skipping Well Location Appendix: " + entry.name,'yellow'))

                #other files to skip
                elif ("dll msfl" in fname.lower()):
                    print(colored("Skipping Log File: " + entry.name,'yellow'))
                elif ("gr_mechanical" in fname.lower()):
                    print(colored("Skipping Log File: " + entry.name,'yellow'))
                elif ("ldl cnl" in fname.lower()):
                    print(colored("Skipping Log File: " + entry.name,'yellow'))
                elif ("pex" in fname.lower()):
                    print(colored("Skipping Log File: " + entry.name,'yellow'))
                elif ("sls" in fname.lower()):
                    print(colored("Skipping Log File: " + entry.name,'yellow'))
                elif ("shot record" in fname.lower()):
                    print(colored("Skipping Shot Record Table: " + entry.name,'yellow'))

                else:
                    print(colored("Processing File: " + entry.name, 'green'))

                    #check if file has equivalent folder (this folder has the jpg files)
                    if(not os.path.isdir(os.path.join(baseFolder, fname))):
                        print(colored("    JPG folder not found.",'red'))
                    else:
                        #report body
                        if("body of rep" in fname.lower() or "body_of_rep" in fname.lower() or "wcr" in fname.lower() or "well completion rep" in fname.lower() or "well_completion_rep" in fname.lower() or "description_of_work" in fname.lower()):
                            #textParseResults = parseJPGs(os.path.join(baseFolder, fname))

                            #for results in textParseResults:
                                #findMarkers(results)
                                #findValues(results)
                            pass

                        #Gas analysis
                        if("coalbed" in fname.lower()):
                            textParseResults = parseJPGs(os.path.join(baseFolder, fname))

                            for results in textParseResults:
                                findMarkers(results)
                                findValues(results)




    global data
    for obj in data:
        print(colored("File: " + obj.file + ", Page: " + obj.page + ", " + obj.valueName + ": " + obj.value, 'white'))


                    #row = [document.filename,os.path.basename(f)[:-4]]
                    #for i in range(len(data[0])-2):
                    #    row.append("null")

                    #count = 0
                    #for item in itemList:
                    #    value = findValue(myTexts,item,layouts[document.layout][item.id])
                    #    row[layouts[document.layout][item.id].column-1] = value
                    #    count = count + 1

                    #if count > 0:
                    #    data.append(row)

    wellFolderContents.close()

    sys.exit()

    with open(dirname + '/' + outputFileName, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerows(data)


    return
#===============================================================


#*********************** FUNCTIONS *******************************
# Function parse JPGs *******************************
def parseJPGs(path):
    results = []

    #iterate through jpg files
    jpgFolderContents = os.scandir(path)

    progress = 0
    myPage = 0
    totalPagesObj = os.scandir(os.path.join(path))
    totalPages = len(list(totalPagesObj))
    print(colored("    Total Pages: " + str(totalPages),'white'))
    totalPagesObj.close()

    for f in jpgFolderContents:
        if f.is_file():
            jpgName, jpgExt = os.path.splitext(f.name)

            if(jpgExt==".jpg"):
                #track progress
                if ((myPage/totalPages*10)-progress) > 1:
                    progress = math.ceil(myPage/totalPages*10)
                    print("    Text Parsing: " + str(progress*10) + "% complete")

                myTexts = detect_text(os.path.join(path, f))

                result = pageText(jpgName,myTexts)
                results.append(result)

                myPage = myPage + 1
    return results
# *************************************************** End Function
# Function to send image to google *******************************
def detect_text(path):
    #print("********* Text Detect - Request Sent *********\n")
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return texts
# *************************************************** End Function
#Function checkText **********************************************
def checkText(mStr, fStr1, fStr2, fStr3, fStr4, fStr5, pStr1, pStr2, pStr3, text, arr, results):
    f1 = False
    f2 = False
    f3 = False
    f4 = False
    f5 = False
    p1 = False
    p2 = False
    p3 = False

    #check
    if (mStr in text.description.lower()):
        if(fStr1 == ""):
            f1 = True
        else:
            fText = followText(fStr1, text, results)
            if fText is not None:
                #print(colored("follow1:" + fText.description,'yellow'))
                if(fStr1 in fText.description.lower()):
                    f1 = True

        if(fStr2 == ""):
            f2 = True
        else:
            if(f1 == True and fText is not None):
                fText = followText(fStr2, fText, results)
                if fText is not None:
                    #print(colored("follow2:" + fText.description,'yellow'))
                    if(fStr2 in fText.description.lower()):
                        f2 = True

        if(fStr3 == ""):
            f3 = True
        else:
            if(f2 == True and fText is not None):
                fText = followText( fStr3, fText, results)
                if fText is not None:
                    #print(colored("follow3:" +fText.description,'yellow'))
                    if(fStr3 in fText.description.lower()):
                        f3 = True

        if(fStr4 == ""):
            f4 = True
        else:
            if(f3 == True and fText is not None):
                fText = followText(fStr4, fText, results)
                if fText is not None:
                    #print(colored("follow4:" + fText.description,'yellow'))
                    if(fStr4 in fText.description.lower()):
                        f4 = True

        if(fStr5 == ""):
            f5 = True
        else:
            if(f4 == True and fText is not None):
                fText = followText(fStr5, fText, results)
                if fText is not None:
                    #print(colored("follow5:" + fText.description,'yellow'))
                    if(fStr5 in fText.description.lower()):
                        f5 = True

        if(pStr1 == ""):
            p1 = True
        else:
            pText = precludeText(pStr1, text, results)
            if pText is not None:
                #print(colored("preclude1: " + pText.description,'yellow'))
                if(pStr1 not in pText.description.lower()):
                    p1 = True
            else:
                p1 = True

        if(pStr2 == ""):
            p2 = True
        else:
            pText = precludeText(pStr2, pText, results)
            if pText is not None:
                #print(colored("preclude2: " + pText.description,'yellow'))
                if(pStr2 not in pText.description.lower()):
                    p2 = True
            else:
                p2 = True

        if(pStr3 == ""):
            p3 = True
        else:
            pText = precludeText(pStr3, pText, results)
            if pText is not None:
                #print(colored("preclude3: " + pText.description,'yellow'))
                if(pStr3 not in pText.description.lower()):
                    p3 = True
            else:
                p3 = True

        #print(colored("f1:"+str(f1)+", f2:"+str(f2)+", f3:"+str(f3)+", f4:"+str(f4)+", f5:"+str(f5)+", p1:"+str(p1)+", p2:"+str(p2)+", p3:"+str(p3),'white'))
        if(f1 and f2 and f3 and f4 and f5 and p1 and p2 and p3):
            foundObj = FoundObj(text.description, text.bounding_poly)
            arr.append(foundObj)

    return arr
# *************************************************** End Function
#Function check following **********************************************
def followText(mStr, mtext, results):
    mFollow = None

    x1 = min(mtext.bounding_poly.vertices[0].x,mtext.bounding_poly.vertices[3].x)
    x2 = max(mtext.bounding_poly.vertices[1].x,mtext.bounding_poly.vertices[2].x)
    y1 = min(mtext.bounding_poly.vertices[0].y,mtext.bounding_poly.vertices[1].y)
    y2 = max(mtext.bounding_poly.vertices[2].y,mtext.bounding_poly.vertices[3].y)

    x = 99999999
    bool = False
    for text in results.texts:
        if(bool):
            tx1 = min(text.bounding_poly.vertices[0].x,text.bounding_poly.vertices[3].x)
            tx2 = max(text.bounding_poly.vertices[1].x,text.bounding_poly.vertices[2].x)
            ty1 = min(text.bounding_poly.vertices[0].y,text.bounding_poly.vertices[1].y)
            ty2 = max(text.bounding_poly.vertices[2].y,text.bounding_poly.vertices[3].y)
            txAve = (tx1+tx2)/2 #average text X
            tyAve = (ty1+ty2)/2 #average text Y

            if(txAve > x1 and txAve > x2 and tyAve > y1 and tyAve < y2 and txAve < x):
                x = txAve
                mFollow = text
        bool = True
    return mFollow
# *************************************************** End Function
#Function check following **********************************************
def precludeText(mStr, mtext, results):
    mPre = None

    x1 = min(mtext.bounding_poly.vertices[0].x,mtext.bounding_poly.vertices[3].x)
    x2 = max(mtext.bounding_poly.vertices[1].x,mtext.bounding_poly.vertices[2].x)
    y1 = min(mtext.bounding_poly.vertices[0].y,mtext.bounding_poly.vertices[1].y)
    y2 = max(mtext.bounding_poly.vertices[2].y,mtext.bounding_poly.vertices[3].y)

    x = 0
    bool = False
    for text in results.texts:
        if(bool):
            tx1 = min(text.bounding_poly.vertices[0].x,text.bounding_poly.vertices[3].x)
            tx2 = max(text.bounding_poly.vertices[1].x,text.bounding_poly.vertices[2].x)
            ty1 = min(text.bounding_poly.vertices[0].y,text.bounding_poly.vertices[1].y)
            ty2 = max(text.bounding_poly.vertices[2].y,text.bounding_poly.vertices[3].y)
            txAve = (tx1+tx2)/2 #average text X
            tyAve = (ty1+ty2)/2 #average text Y

            if(txAve < x1 and txAve < x2 and tyAve > y1 and tyAve < y2 and txAve > x):
                x = txAve
                mPre = text
        bool = True
    return mPre
# *************************************************** End Function
#Function findMarkers ********************************************
def findMarkers(results):
    global foundLats, foundLongs
    foundLats = []
    foundLongs = []

    global foundSeam
    global foundTops
    global foundBots
    global foundNets
    foundSeam = []
    foundTops = []
    foundBots = []
    foundNets = []

    global foundQ1Raw
    global foundQ2Raw
    global foundQ3Raw
    global foundQtRaw
    foundQ1Raw = []
    foundQ2Raw = []
    foundQ3Raw = []
    foundQtRaw = []

    global foundQ1Daf
    global foundQ2Daf
    global foundQ3Daf
    global foundQtDaf
    foundQ1Daf = []
    foundQ2Daf = []
    foundQ3Daf = []
    foundQtDaf = []

    bool = False
    for text in results.texts:
        if(bool):
            #checkText(mStr, fStr1, fStr2, fStr3, fStr4, fStr5, pStr1, pStr2, pStr3, text, arr, results)
            foundLats = checkText ("latitude", "", "", "", "", "", "", "", "", text, foundLats, results)
            foundLongs = checkText ("longitude", "", "", "", "", "", "", "", "", text, foundLongs, results)
            foundLongs = checkText ("longtitude", "", "", "", "", "", "", "", "", text, foundLongs, results)

            foundSeam = checkText ("coal", "", "", "", "", "", "", "", "", text, foundSeam, results)
            foundTops = checkText ("top", "(m", "", "", "", "", "", "", "", text, foundTops, results)
            foundBots = checkText ("base", "(m", "", "", "", "", "", "", "", text, foundBots, results)
            foundNets = checkText ("net", "(m", "", "", "", "", "", "", "", text, foundNets, results)
            foundNets = checkText ("gross", "(m", "", "", "", "", "", "", "", text, foundNets, results)

            foundQ1Raw = checkText("lost", "gas", "scc/g", "", "", "", "daf", "", "", text, foundQ1Raw, results) #Lost gas
            foundQ2Raw = checkText("raw", "desorb", "gas", "scc/g", "", "", "", "", "", text, foundQ2Raw, results) #Desorbed gas
            foundQ3Raw = checkText("residual", "gas", "scc/g", "", "", "", "daf", "", "", text, foundQ3Raw, results) #Gas on Crushing
            foundQtRaw = checkText("total", "raw", "gas", "scc/g", "", "", "", "", "", text, foundQtRaw, results) #Total

            foundQ1Daf = checkText("daf", "lost", "gas", "scc/g", "", "", "", "", "", text, foundQ1Daf, results) #Lost gas
            foundQ2Daf = checkText("daf", "desorb", "gas", "scc/g", "", "", "", "", "", text, foundQ2Daf, results) #Desorbed gas
            foundQ3Daf = checkText("daf", "residual", "gas", "", "", "", "", "", "", text, foundQ3Daf, results) #Gas on Crushing
            foundQtDaf = checkText("daf", "total", "gas", "", "", "", "", "", "", text, foundQtDaf, results) #Total
        bool = True
# *************************************************** End Function
#Function findValues ***********************************************
def findValues(results):
    global data

    global valuesLat
    global valuesLong
    valuesLat = []
    valuesLong = []

    global valuesTop
    global valuesBot
    global valuesNet
    valuesTop = []
    valuesBot = []
    valuesNet = []

    global foundQ1Raw
    global foundQ2Raw
    global foundQ3Raw
    global foundQtRaw
    global vQ1Raw
    global vQ2Raw
    global vQ3Raw
    global vQtRaw
    vQ1Raw = []
    vQ2Raw = []
    vQ3Raw = []
    vQtRaw = []

    global foundQ1Daf
    global foundQ2Daf
    global foundQ3Daf
    global foundQtDaf
    global vQ1Daf
    global vQ2Daf
    global vQ3Daf
    global vQtDaf
    vQ1Daf = []
    vQ2Daf = []
    vQ3Daf = []
    vQtDaf = []

    for text in results.texts:
        tx1 = min(text.bounding_poly.vertices[0].x,text.bounding_poly.vertices[3].x)
        tx2 = max(text.bounding_poly.vertices[1].x,text.bounding_poly.vertices[2].x)
        ty1 = min(text.bounding_poly.vertices[0].y,text.bounding_poly.vertices[1].y)
        ty2 = max(text.bounding_poly.vertices[2].y,text.bounding_poly.vertices[3].y)
        txAve = (tx1+tx2)/2 #average text X
        tyAve = (ty1+ty2)/2 #average text Y

        latitude(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #LATITUDE
        longitude(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #LONGITUDE

        top(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #TOPs
        bot(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #Bottoms
        net(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #Net Coal

        vQ1Raw = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQ1Raw,vQ1Raw) #Q1 Raw Gas (Desorbed)
        vQ2Raw = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQ2Raw,vQ2Raw) #Q2 Raw Gas (Desorbed)
        vQ3Raw = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQ3Raw,vQ3Raw) #Q3 Raw Gas (Crushing)
        vQtRaw = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQtRaw,vQtRaw) #Total Raw Gas

        vQ1Daf = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQ1Daf,vQ1Daf) #Q1 Daf Gas (Desorbed)
        vQ2Daf = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQ2Daf,vQ2Daf) #Q2 Daf Gas (Desorbed)
        vQ3Daf = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQ3Daf,vQ3Daf) #Q3 Daf Gas (Crushing)
        vQtDaf = addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,foundQtDaf,vQtDaf) #Total Daf Gas

    valuesLat = sorted(valuesLat)
    valuesLong = sorted(valuesLong)

    redo = False
    redoLat = False
    redoLong = False

    if(len(valuesLat)>0):
        if(valuesLat[0].text.lower() == "(s)" or "longitude" in valuesLat[0].text.lower()):
            valuesLat = []
            redoLat = True
            redo = True


    if(len(valuesLong)>0):
        if(valuesLong[0].text.lower() == "(e)"):
            valuesLong = []
            redoLong = True
            redo = True

    if(redo):
        for text in results.texts:
            tx1 = min(text.bounding_poly.vertices[0].x,text.bounding_poly.vertices[3].x)
            tx2 = max(text.bounding_poly.vertices[1].x,text.bounding_poly.vertices[2].x)
            ty1 = min(text.bounding_poly.vertices[0].y,text.bounding_poly.vertices[1].y)
            ty2 = max(text.bounding_poly.vertices[2].y,text.bounding_poly.vertices[3].y)
            txAve = (tx1+tx2)/2 #average text X
            tyAve = (ty1+ty2)/2 #average text Y

            latitude2(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #LATITUDE
            longitude2(results,text,tx1,tx2,ty1,ty2,txAve,tyAve) #LONGITUDE

    valuesLat = sorted(valuesLat)
    valuesLong = sorted(valuesLong)

    for i in range(len(valuesLat)):
        if(valuesLat[i].text[-1].lower() == "s" or "south" in valuesLat[i].text[-1].lower()):
            for j in range((len(valuesLat)-i-1)):
                valuesLat.pop()
            break

    for i in range(len(valuesLong)):
        if(valuesLong[i].text[-1].lower() == "e" or valuesLong[i].text[-1].lower() == "east"):
            for j in range((len(valuesLong)-i-1)):
                valuesLong.pop()
            break

    mStr = concatData(valuesLat)
    if(mStr != ""):
        addData(wellname,results.pageFileName,"Latitude",mStr)
    mStr = concatData(valuesLong)
    if(mStr != ""):
        addData(wellname, results.pageFileName,"Longitude",mStr)

    for value in valuesTop:
        addData(wellname ,results.pageFileName,"Top",value.text)
    for value in valuesBot:
        addData(wellname ,results.pageFileName,"Bottom",value.text)
    for value in valuesNet:
        addData(wellname ,results.pageFileName,"Net Coal",value.text)

    for value in vQ1Raw:
        addData(wellname ,results.pageFileName,"Q1 Raw Gas",value.text)
    for value in vQ2Raw:
        addData(wellname ,results.pageFileName,"Q2 Raw Gas",value.text)
    for value in vQ3Raw:
        addData(wellname ,results.pageFileName,"Q3 Raw Gas",value.text)
    for value in vQtRaw:
        addData(wellname ,results.pageFileName,"Total Raw Gas",value.text)

    for value in vQ1Daf:
        addData(wellname ,results.pageFileName,"Q1 DAF Gas",value.text)
    for value in vQ2Daf:
        addData(wellname ,results.pageFileName,"Q2 DAF Gas",value.text)
    for value in vQ3Daf:
        addData(wellname ,results.pageFileName,"Q3 DAF Gas",value.text)
    for value in vQtDaf:
        addData(wellname ,results.pageFileName,"Total DAF Gas",value.text)
# *************************************************** End Function

class ValueObj(object):
    def __init__(self, x, y, text):
        self.x = x          #x average
        self.y = y          #y average
        self.text = text    #found text

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.text == other.text

    def __lt__(self, other):
        return self.x < other.x
class FoundObj(object):
    def __init__(self, description, bounding_poly):
        self.description = description
        self.bounding_poly = bounding_poly
        self.xMax = None
        self.yMax = None
        self.valueId = None

    def __eq__(self, other):
        return self.description == other.description and self.bounding_poly == other.bounding_poly and self.xMax == other.xMax and self.yMax == other.yMax and self.valueId == other.valueId

    def __lt__(self, other):
        return self.xMax < other.xMax
class DataObj(object):
    def __init__(self, file, page, valueName, value):
        self.file = file
        self.page = page
        self.valueName = valueName
        self.value = value

    def __eq__(self, other):
        return self.file == other.file and self.page == other.page and self.valueName == other.valueName and self.value == other.value

    def __lt__(self, other):
        return self.page < other.page
# *************************************************** End Function
#Function Concatonate ********************************************
def addData(fileName,pageName,valueName, value):
    dataObj = DataObj(fileName, pageName, valueName, value)
    data.append(dataObj)
    return
# *************************************************** End Function
#Function Concatonate ********************************************
def concatData(arr):
    mStr = ""
    a = False
    for value in arr:
        if(a):
            mStr += " "
        mStr += value.text
        a = True

    return mStr
# *************************************************** End Function
#Function latitude************************************************
def addFirstValueRIGHT(results,text,tx1,tx2,ty1,ty2,txAve,tyAve,arrF,arrV):
    for item in arrF: #MARKER Coordinates
        if (item.xMax is None):
            xMax = 99999999
        else:
            xMax = item.xMax

        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)

        if(txAve > x2 and tyAve > y1 and tyAve < y2 and isNumber(text.description) and txAve < xMax):
            valueObj = ValueObj(txAve,tyAve,text.description)
            arrV.append(valueObj)
            if(item.valueId is not None):
                arrV.pop(item.valueId)
            item.xMax = txAve
            item.valueId = len(arrV)-1

    #result = [arrF,arrV]
    return arrV
# *************************************************** End Function
#Function latitude************************************************
def latitude(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesLat

    for item in foundLats: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)

        if(txAve > x2 and tyAve > y1 and tyAve < y2):
            valueObj = ValueObj(txAve,tyAve,text.description)
            valuesLat.append(valueObj)
    return
# *************************************************** End Function
#Function latitude2***********************************************
def latitude2(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesLat
    for item in foundLats: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)
        dx = x2 - x1
        dy = y2 - y1

        xmin = x1
        xmax = x2 + 2*dx
        ymin = (y1+y2)/2
        ymax = y2 + 2*dy

        if(tx1 > xmin and tx1 < xmax and ty1 > ymin and ty2 < ymax):
            valueObj = ValueObj(txAve,tyAve,text.description)
            valuesLat.append(valueObj)
    return
# *************************************************** End Function
#Function Longitude***********************************************
def longitude(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesLong

    for item in foundLongs: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)

        if(txAve > x2 and tyAve > y1 and tyAve < y2):
            valueObj = ValueObj(txAve,tyAve,text.description)
            valuesLong.append(valueObj)
    return
# *************************************************** End Function
#Function longitude2**********************************************
def longitude2(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesLat
    for item in foundLongs: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)
        dx = x2 - x1
        dy = y2 - y1

        xmin = x1
        xmax = x2 + 2*dx
        ymin = (y1+y2)/2
        ymax = y2 + 2*dy

        if(tx1 > xmin and tx1 < xmax and ty1 > ymin and ty2 < ymax):
            valueObj = ValueObj(txAve,tyAve,text.description)
            valuesLong.append(valueObj)
    return
# *************************************************** End Function
#Function Tops****************************************************
def top(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesTop
    for item in foundTops: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)
        dx = x2 - x1
        dy = y2 - y1

        xmin = x1
        xmax = x2
        ymin = y2
        ymax = 99999999

        if(tx1 > xmin and tx1 < xmax and ty1 > ymin and ty2 < ymax):
            seamName = "Seam Name Extract Failed"
            for adText in results.texts:
                coalCheck = False
                adx1 = min(adText.bounding_poly.vertices[0].x,adText.bounding_poly.vertices[3].x)
                adx2 = max(adText.bounding_poly.vertices[1].x,adText.bounding_poly.vertices[2].x)
                ady1 = min(adText.bounding_poly.vertices[0].y,adText.bounding_poly.vertices[1].y)
                ady2 = max(adText.bounding_poly.vertices[2].y,adText.bounding_poly.vertices[3].y)
                adxave = (adx1 + adx2)/2
                adyave = (ady1 + ady2)/2
                addx = adx2 - adx1
                addy = ady2 - ady1
                adxmin = adx1 - 2*addx
                adxmax = adx2 + 2* addx

                for seam in foundSeam:
                    sx1 = min(seam.bounding_poly.vertices[0].x,seam.bounding_poly.vertices[3].x)
                    sx2 = max(seam.bounding_poly.vertices[1].x,seam.bounding_poly.vertices[2].x)
                    sy1 = min(seam.bounding_poly.vertices[0].y,seam.bounding_poly.vertices[1].y)
                    sy2 = max(seam.bounding_poly.vertices[2].y,seam.bounding_poly.vertices[3].y)
                    sxave = (sx1 + sx2)/2
                    syave = (sy1 + sy2)/2
                    sdx = sx2 - sx1
                    sdy = sy2 - sy1
                    sxmin = sx1 - 2*sdx
                    sxmax = sx2 + 2* sdx

                    if(adxave > sxmin and adxave < sxmax and adyave > sy2):
                        if(adyave > ty1 and adyave < ty2):
                            seamName = adText.description


            valueObj = ValueObj(txAve,tyAve,seamName + ": " + text.description)
            valuesTop.append(valueObj)
    return
# *************************************************** End Function
#Function Bottoms*************************************************
def bot(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesBot
    for item in foundBots: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)
        dx = x2 - x1
        dy = y2 - y1

        xmin = x1
        xmax = x2
        ymin = y2
        ymax = 99999999

        if(tx1 > xmin and tx1 < xmax and ty1 > ymin and ty2 < ymax):
            seamName = "Seam Name Extract Failed"
            for adText in results.texts:
                coalCheck = False
                adx1 = min(adText.bounding_poly.vertices[0].x,adText.bounding_poly.vertices[3].x)
                adx2 = max(adText.bounding_poly.vertices[1].x,adText.bounding_poly.vertices[2].x)
                ady1 = min(adText.bounding_poly.vertices[0].y,adText.bounding_poly.vertices[1].y)
                ady2 = max(adText.bounding_poly.vertices[2].y,adText.bounding_poly.vertices[3].y)
                adxave = (adx1 + adx2)/2
                adyave = (ady1 + ady2)/2
                addx = adx2 - adx1
                addy = ady2 - ady1
                adxmin = adx1 - 2*addx
                adxmax = adx2 + 2* addx

                for seam in foundSeam:
                    sx1 = min(seam.bounding_poly.vertices[0].x,seam.bounding_poly.vertices[3].x)
                    sx2 = max(seam.bounding_poly.vertices[1].x,seam.bounding_poly.vertices[2].x)
                    sy1 = min(seam.bounding_poly.vertices[0].y,seam.bounding_poly.vertices[1].y)
                    sy2 = max(seam.bounding_poly.vertices[2].y,seam.bounding_poly.vertices[3].y)
                    sxave = (sx1 + sx2)/2
                    syave = (sy1 + sy2)/2
                    sdx = sx2 - sx1
                    sdy = sy2 - sy1
                    sxmin = sx1 - 2*sdx
                    sxmax = sx2 + 2* sdx

                    if(adxave > sxmin and adxave < sxmax and adyave > sy2):
                        if(adyave > ty1 and adyave < ty2):
                            seamName = adText.description


            valueObj = ValueObj(txAve,tyAve,seamName + ": " + text.description)
            valuesBot.append(valueObj)
    return
# *************************************************** End Function
#Function Net Coal************************************************
def net(results,text,tx1,tx2,ty1,ty2,txAve,tyAve):
    global valuesNet
    for item in foundNets: #MARKER Coordinates
        x1 = min(item.bounding_poly.vertices[0].x,item.bounding_poly.vertices[3].x)
        x2 = max(item.bounding_poly.vertices[1].x,item.bounding_poly.vertices[2].x)
        y1 = min(item.bounding_poly.vertices[0].y,item.bounding_poly.vertices[1].y)
        y2 = max(item.bounding_poly.vertices[2].y,item.bounding_poly.vertices[3].y)
        dx = x2 - x1
        dy = y2 - y1

        xmin = x1 - dx*4
        xmax = x2 + dx*4
        ymin = y2
        ymax = 99999999

        if(tx1 > xmin and tx1 < xmax and ty1 > ymin and ty2 < ymax):
            seamName = "Seam Name Extract Failed"
            for adText in results.texts:
                coalCheck = False
                adx1 = min(adText.bounding_poly.vertices[0].x,adText.bounding_poly.vertices[3].x)
                adx2 = max(adText.bounding_poly.vertices[1].x,adText.bounding_poly.vertices[2].x)
                ady1 = min(adText.bounding_poly.vertices[0].y,adText.bounding_poly.vertices[1].y)
                ady2 = max(adText.bounding_poly.vertices[2].y,adText.bounding_poly.vertices[3].y)
                adxave = (adx1 + adx2)/2
                adyave = (ady1 + ady2)/2
                addx = adx2 - adx1
                addy = ady2 - ady1
                adxmin = adx1 - 2*addx
                adxmax = adx2 + 2* addx

                for seam in foundSeam:
                    sx1 = min(seam.bounding_poly.vertices[0].x,seam.bounding_poly.vertices[3].x)
                    sx2 = max(seam.bounding_poly.vertices[1].x,seam.bounding_poly.vertices[2].x)
                    sy1 = min(seam.bounding_poly.vertices[0].y,seam.bounding_poly.vertices[1].y)
                    sy2 = max(seam.bounding_poly.vertices[2].y,seam.bounding_poly.vertices[3].y)
                    sxave = (sx1 + sx2)/2
                    syave = (sy1 + sy2)/2
                    sdx = sx2 - sx1
                    sdy = sy2 - sy1
                    sxmin = sx1 - 2*sdx
                    sxmax = sx2 + 2* sdx

                    if(adxave > sxmin and adxave < sxmax and adyave > sy2):
                        if(adyave > ty1 and adyave < ty2):
                            seamName = adText.description


            valueObj = ValueObj(txAve,tyAve,seamName + ": " + text.description)
            valuesNet.append(valueObj)
    return
# *************************************************** End Function

#Function isNumber ***********************************************
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
# *************************************************** End Function


#===============================================================


#*********************** CLASSES *******************************
# Coordinate Class *********************************************
class Coord:
    def __init__(self,id,text,x1,x2,y1,y2):
        self.id = id
        self.text = text
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def printMe(self):
        print('    Text: "%s"\n        x1: %s\n        x2: %s\n        y1: %s\n        y2: %s' % (self.text, self.x1, self.x2, self.y1, self.y2))
#***************************************************** End Class
# File List Class **********************************************
class Files:
    def __init__(self,filename,startPage,endPage,layout):
        self.filename = filename
        self.startPage = startPage
        self.endPage = endPage
        self.layout = layout
#***************************************************** End Class
# Layout Class **********************************************
class LayoutValue:
    def __init__(self,name,column,text,alternate,direction,type,min,max,preclude):
        self.name = name
        self.column = column
        self.text = text
        self.alternate = alternate
        self.direction = direction
        self.type = type
        self.min = min
        self.max = max
        self.preclude = preclude
#***************************************************** End Class
# Data Class **********************************************
class DataPoint:
    def __init__(self,name,column,value):
        self.name = name
        self.column = column
        self.value = value
#***************************************************** End Class
# Data Class **********************************************
class pageText:
    def __init__(self,pageFileName,texts):
        self.pageFileName = pageFileName
        self.texts = texts
#***************************************************** End Class
#===============================================================


main()
print(colored("\n********* END RUN *********",'green'))
