from django.conf import settings

# Other module imports.
from data_extraction.models import *
from data_extraction.functions import *
from file_manager import fileModule

from data_extraction.responseCodes import Result, GenerateResult, PrintResultLog, convertList as resultList
from data_extraction.functions import IsNumber

# Third party imports.
import os
import io
from PIL import Image #pip install Pillow
from pdf2image import convert_from_path #pip install pdf2image and install poppler and add to PATH (https://pypi.org/project/pdf2image/)
import tempfile

from decimal import Decimal

# Imports the Google Cloud client library
from google.cloud import vision
from google.protobuf.json_format import MessageToJson

def ExtractPages(document, firstPage, lastPage, delete):
    ext = GetDocumentExt(document)

    if delete:
        for page in document.pages.all():
            page.file.delete()
            page.delete()

    if ext == "tiff" or ext == ".tif" or ext == ".pdf":
        if document.conversion_status == document.NOTCONVERTED:
            if(document.status != document.DOWNLOADED):
                #print("Document Status: " + document.get_status_display())
                result = fileModule.downloadDocument(document)
                if(result.code != "00000" and result.code != "50005"):
                    # Failed, notify users
                    #print("file not downloaded")
                    print(result.code)
                    return result
                else:
                    # Success
                    document.status = document.DOWNLOADED
                    document.save()

            documentPath = settings.MEDIA_ROOT + document.file.file_location + document.file.file_name + document.file.file_ext

            # Document Folder
            documentFolder = document.file.file_location + document.file.file_name + '/'
            result = fileModule.makeDirectory(documentFolder, settings.USE_S3)
            if result.code != "00000":
                return result

            # Images Folder
            imageFolder = document.file.file_location + document.file.file_name + '/images/'
            result = fileModule.makeDirectory(imageFolder, settings.USE_S3)
            if result.code != "00000":
                return result

            imagePath = settings.MEDIA_ROOT + imageFolder

            # PARSE TIF FILES
            if ext == "tiff" or ext == ".tif":
                success = True
                try:
                    #open tif
                    im = Image.open(documentPath)

                    #loop through pages
                    min = 0
                    max = 1000
                    if firstPage is not None:
                        min = firstPage - 1
                    if lastPage is not None:
                        max = lastPage - 1
                    for i in range(min,max):
                        if(i == 999):
                            print("Warning: reached 1000 pages in file %s" % name)
                        try:
                            #load page
                            im.seek(i)
                            outfile = imagePath + '/page' + str(i+1) + '.jpg'
                            try:
                                im.thumbnail(im.size)
                                im.save(outfile, "JPEG", quality=100)
                            except:
                                print("failed to create JPEG: " + outfile)
                                success = False
                        except EOFError:
                            # Not enough frames in img
                            print("Not enough frames in img")
                            success = False
                            break
                except Exception as e:
                    print("Failed to open: " + imagePath + ". Image is probably too large.")
                    print(e)
                    success = False
                
                if(success):
                    if firstPage is None and lastPage is None:
                        document.conversion_status = document.CONVERTED
                        document.save()      

            #PARSE PDF FILES********************************************************************************************
            elif ext == ".pdf":
                with tempfile.TemporaryDirectory() as path:
                    #create pages
                    success = False
                    try:
                        pages = convert_from_path(
                            documentPath, 
                            dpi=150,
                            output_folder=path,
                            first_page=firstPage,
                            last_page=lastPage,
                        )
                        success = True
                    except Exception as e:
                        #print("File too large")
                        print(e)
                        success = False

                    if(success):
                        #save pages
                        i = 1
                        for page in pages:
                            filename = imagePath + 'page' + str(i) + ".jpg"
                            page.save(filename, 'JPEG')

                            # Create page object
                            oPage = Page.objects.filter(document=document, page_no=i).first()
                            if oPage is None:
                                try:
                                    fileSize = os.path.getsize(imagePath)
                                    file = File.objects.create(
                                        file_name = 'page' + str(i),
                                        file_ext =  ".jpg",
                                        file_location = imageFolder,
                                        file_size = fileSize
                                    )
                                    oPage = Page.objects.create(
                                        document = document,
                                        page_no = i,
                                        file = file,
                                        extracted = False
                                    )
                                except Exception as e:
                                    print(e)     
                                    success = False                   

                            i = i + 1

                    if(success):
                        if firstPage is None and lastPage is None:
                            document.conversion_status = document.CONVERTED
                            document.save()        

    else:
        document.conversion_status = document.IGNORED
        document.save()        

    result = GenerateResult(resultList,0)
    return result
    
def getDocumentText(document):
    pages = Page.objects.filter(document = document, extracted = False).all()

    for page in pages:
        if not page.extracted:
            file = page.file
            path = file.path()

            pageTexts = getTextArray(path)

            i = 0
            for pageText in pageTexts:
                i = i + 1
                if(len(pageText.description) > 255):
                    #print(str(i) + ": " + pageText.description)
                    pass
                else:
                    text = Text.objects.create(
                        page = page,
                        text = pageText.description
                    )
                    bps = pageText.bounding_poly


                    for i in range(4):
                        x = int(bps.vertices[i].x)
                        y = int(bps.vertices[i].y)
                        BoundingPoly.objects.create(
                            text = text,
                            x = x,
                            y = y
                        )
            
            page.extracted = True
            page.save()

    result = GenerateResult(resultList,0)
    return result

def getTextArray(path):
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return texts


def ExtractData(document,method):
    pages = document.pages.all()

    for page in pages:
        texts = page.texts.all()
        for text in texts:
            if (method.mStr.lower() in text.text.lower()):
                lastText = text
                text1 = None
                text2 = None

                # Value Start = Follow
                if method.value_start == method.FIRST:
                    text1 = lastText

                # Check Following
                success = True
                if method.fStr1 is not None:
                    checkStr = strReduce(method.fStr1)
                    success = False
                    foundStr = ""
                    for i in range(10):
                        result = followText(lastText, None, page)
                        if result.code != "00000":
                            fText = None
                        else:
                            fText = result.text
                        if fText is None:
                            break
                        lastText = fText
                        foundStr += strReduce(fText.text)
                        #print(foundStr)

                        if foundStr == checkStr:
                            success = True
                            break

                    # Value Start = Follow
                    if method.value_start == method.FOLLOW or method.value_start == method.AVEFOLLOWLASTBELOW:
                        text1 = lastText

                if success == False:
                    continue
                

                # Check Below
                success = True
                lastBelowText = None
                if method.bStr1 is not None:
                    checkStr = strReduce(method.bStr1)
                    success = False

                    result = belowText(text, page)
                    if result.code != "00000":
                        bText = None
                    else:
                        bText = result.text

                    lastText = bText
                    foundStr = strReduce(bText.text)

                    for i in range(10):
                        #print(foundStr)
                        if foundStr == checkStr:
                            success = True
                            # Value Start = Last Below
                            if method.value_start == method.LASTBELOW:
                                text1 = lastText
                            # Value Start = average of follow and last below
                            if method.value_start == method.AVEFOLLOWLASTBELOW:
                                text2 = lastText
                            break

                        result = followText(lastText, None, page)
                        if result.code != "00000":
                            fText = None
                        else:
                            fText = result.text
                        if fText is None:
                            break
                        lastText = fText
                        foundStr += strReduce(fText.text)

                        # Value Start = First Below
                        if i == 0:
                            if method.value_start == method.FIRSTBELOW:
                                text1 = lastText

                if success == False:
                    continue
                

                # Check Precluding


                # Get Value
                result = getValueText(method, page, text1, text2)
                
                    
                    

    result = GenerateResult(resultList,0)
    return result

def strReduce(str):
    if str is None:
        return str
    return str.replace(" ","").replace(")","").replace("(","").replace("|","").lower()

def getValueText(method, page, text1, text2):
    #print(f"Method ID: {method.id}")
    #print(f"Page: {page}")
    #print(f"Text1: {text1}")
    #print(f"Text2: {text2}")

    success = False
    if text1 is not None and text2 is None:
        if method.value_direction == method.RIGHT:
            result = followText(text1, None, page)
            success = True
        if method.value_direction == method.DOWN:
            result = belowText(text1, page)
            success = True
        # ***
        # Complete other directions
        # ***

    if text1 is not None and text2 is not None:
        result = followText(text1, text2, page)
        success = True

    if success:
        if result.text is not None:
            #print(f"Send to value: {result.text.text}")
            if result.code != "00000":
                return result
            else:
                if result.text is not None:
                    return getValue(result.text, method, page)
        else:
            return None
    else:
        return None

def followText(text, text2, page):
    result = processPoly(text)
    if result.code != "00000":
        result.text = None
        return result
    else:
        poly = result.poly

    if text2 is not None:
        result2 = processPoly(text2)
        if result2.code != "00000":
            result.text = None
            return result2
        else:
            poly2 = result2.poly

        poly1 = poly
        poly = {
            'x1' : min(poly1['x1'],poly2['x1']),
            'x2' : max(poly1['x2'],poly2['x2']),
            'y1' : min(poly1['y1'],poly2['y1']),
            'y2' : max(poly1['y2'],poly2['y2']),
            'xdif' : max(poly1['x2'],poly2['x2']) - min(poly1['x1'],poly2['x1']),
            'ydif' : max(poly1['y2'],poly2['y2']) - min(poly1['y1'],poly2['y1']),
            'xave' : (min(poly1['x1'],poly2['x1']) + max(poly1['x2'],poly2['x2']))/2,
            'yave' : (min(poly1['y1'],poly2['y1']) + max(poly1['y2'],poly2['y2']))/2,
        }

    texts = Text.objects.filter(
        page = page,
        BoundingPolys__x__gte = poly['x2'],
        BoundingPolys__y__gte = (poly['y1']-poly['ydif']/2),
        BoundingPolys__y__lte = (poly['y2']+poly['ydif']/2),
    )
    texts = texts.exclude(text="(")
    texts = texts.exclude(text=")")
    texts = texts.exclude(text="|")
    texts = texts.distinct()

    x = 9999999
    fText = None
    
    for t in texts:
        if t != text and t!= text2:
            result = processPoly(t)
            if result.code == "00000":
                testPoly = result.poly

                # Check poly is in correct y boundary
                if testPoly['y1']<poly['yave'] and testPoly['y2']>poly['yave']:
                    # Check x is greater than starting poly and is the smallest that has been found
                    if testPoly['xave'] > poly['x2'] and testPoly['xave'] < x:
                        x = testPoly['xave']
                        fText = t

    result = GenerateResult(resultList,0)
    result.text = fText
    return result

def belowText(text, page):
    result = processPoly(text)
    if result.code != "00000":
        result.text = None
        return result
    else:
        poly = result.poly

    texts = Text.objects.filter(
        page = page,
        BoundingPolys__y__gte = poly['yave'],
        BoundingPolys__x__gte = (poly['x1']-poly['xdif']/2),
        BoundingPolys__x__lte = (poly['x2']+poly['xdif']/2),
    )
    texts = texts.exclude(text="(")
    texts = texts.exclude(text=")")
    texts = texts.exclude(text="|")
    texts = texts.distinct()

    y = 9999999
    x = 9999999
    bText = None
    
    for t in texts:
        if t != text:
            result = processPoly(t)
            if result.code == "00000":
                testPoly = result.poly

                # Check poly is in correct x boundary
                if poly['x1']<testPoly['xave']:
                    # Check y is greater than starting poly and is the smallest by far
                    if testPoly['yave'] > poly['y2'] and testPoly['yave'] < (y - testPoly['ydif']/2):
                        y = testPoly['yave']
                        x = testPoly['xave']
                        bText = t
                    # Else if it is greater than starting poly and is the smallest or close to
                    elif testPoly['yave'] > poly['y2'] and testPoly['yave'] < (y + testPoly['ydif']/2):
                        # Check if x is smallest
                        if testPoly['xave'] < x:
                            y = testPoly['yave']
                            x = testPoly['xave']
                            bText = t

    result = GenerateResult(resultList,0)
    result.text = bText
    return result

def processPoly(text):
    polys = text.BoundingPolys.all()
    if polys.count() != 4:
        result = GenerateResult(resultList,15)
        result.consolLog = f"{result.consolLog} Poly Count: {polys.count()}"
        PrintResultLog(result)
        return result
    
    BL = polys[0]
    BR = polys[0]
    TL = polys[0]
    TR = polys[0]

    for i in range(4):
        poly = polys[i]
        if poly.y >= BL.y:
            BR = BL
            BL = poly
        elif poly.y >= BR.y:
            BR = poly

        if poly.y <= TL.y:
            TR = TL
            TL = poly
        elif poly.y <= TR.y:
            TR = poly

    if BL.x > BR.x:
        temp = BR
        BR = BL
        BL = temp

    if TL.x > TR.x:
        temp = TR
        TR = TL
        TL = temp

    x1 = min(BL.x,TL.x)
    x2 = max(BR.x,TR.x)
    y1 = min(TL.y,TR.y)
    y2 = max(BL.y,BR.y)
    xdif = (x2-x1)
    ydif = (y2-y1)
    xave = (x1+x2)/2
    yave = (y1+y2)/2

    poly = {
        'BL' : BL,
        'BR' : BR,
        'TL' : TL,
        'TR' : TR,
        'x1' : x1,
        'x2' : x2,
        'y1' : y1,
        'y2' : y2,
        'xdif' : xdif,
        'ydif' : ydif,
        'xave' : xave,
        'yave' : yave,
    }

    result = GenerateResult(resultList,0)
    result.poly = poly
    return result


def getValue(text, method, page):
    #print(f"Method: {method.name}")
    valueText = text.text
    #print(valueText)

    success = True
    endCut = 0
    lastText = text

    # check follow string
    if method.fStr2 is not None:
        #print(f"Follow String: {method.fStr2}")
        checkStr = strReduce(method.fStr2)
        success = False

        test1 = False
        if len(valueText) > len(checkStr):
            if valueText[-1*len(checkStr):] == checkStr:
                success = True
                endCut = -1*len(checkStr)
                test1 = True
        if not test1:
            result = followText(text, None, page)
            if result.code != "00000":
                fText = None
            else:
                fText = result.text
            if fText is not None:
                foundStr = strReduce(fText.text)
                if foundStr == checkStr:
                    success = True
                    lastText = fText

    # check additional follow string
    if success:
        if method.fStr3 is not None: 
            checkStr = strReduce(method.fStr3)
            success = False
            foundStr = ""
            for i in range(10):
                result = followText(lastText, None, page)
                if result.code != "00000":
                    fText = None
                else:
                    fText = result.text
                if fText is None:
                    break
                lastText = fText
                foundStr += strReduce(fText.text)
                if foundStr == checkStr:
                    success = True
                    break

    if success:
        if endCut != 0:
            valueText = valueText[:endCut]
        if not IsNumber(valueText) and valueText[-3] == ',':
            valueText=valueText[:-3] + '.' + valueText[-2:]
        if IsNumber(valueText):
            try:
                value = Decimal(valueText)
                # Rotary Table
                if method.dataType == method.ROTARYTABLE:
                    #print(f"Rotary Table: {value}")
                    data = Data_RotaryTable.objects.filter(
                        page=page,
                        value = value,
                        unit=method.unit
                    ).first()
                    if data is None:
                        data = Data_RotaryTable.objects.create(
                            page=page,
                            extraction_method = method,
                            value = value,
                            unit=method.unit
                        )

                # Total Depth   
                if method.dataType == method.TOTALDEPTH:
                    #print(f"Total Depth: {value}")
                    data = Data_TotalDepth.objects.filter(
                        page=page,
                        value = value,
                        unit=method.unit
                    ).first()
                    if data is None:
                        data = Data_TotalDepth.objects.create(
                            page=page,
                            extraction_method = method,
                            value = value,
                            unit=method.unit
                        )

                # Ground Elevation
                if method.dataType == method.GROUNDELEVATION:
                    #print(f"Gound Level: {value}")
                    data = Data_GroundElevation.objects.filter(
                        page=page,
                        value = value,
                        unit=method.unit
                    ).first()
                    if data is None:
                        data = Data_GroundElevation.objects.create(
                            page=page,
                            extraction_method = method,
                            value = value,
                            unit=method.unit
                        )
            except Exception as e:
                print(e)

