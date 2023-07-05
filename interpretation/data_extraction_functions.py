from django.conf import settings
from django.db.models import Q

# Other module imports.
from data_extraction.models import *
from data_extraction.functions import *
from file_manager import fileModule

from data_extraction.responseCodes import Result, GenerateResult, PrintResultLog, convertList as resultList
from data_extraction.functions import IsNumber

# Python imports
from decimal import Decimal
import re

# Third party imports.
import os
import io
from PIL import Image #pip install Pillow
from pdf2image import convert_from_path #pip install pdf2image and install poppler and add to PATH (https://pypi.org/project/pdf2image/)
import tempfile

# Imports the Google Cloud client library
from google.cloud import vision
from google.protobuf.json_format import MessageToJson

# Logging
import logging
log = logging.getLogger("interpretation")

def ExtractPages(document, firstPage, lastPage, delete):
    log.debug('Extracting Pages for Well: %s, Document %s (%i).', document.well.well_name, document.document_name, document.id)
    ext = GetDocumentExt(document)
    success = False

    if document.conversion_status == document.CONVERTED:
        result = GenerateResult(resultList,0)
        return result
    if delete:
        for page in document.pages.all():
            page.file.delete()
            page.delete()
        document.conversion_status = document.NOTCONVERTED
        document.save()

    if ext == "tiff" or ext == ".tif" or ext == ".pdf":
        if document.status != document.DOWNLOADED or not document.file:
            result = fileModule.downloadWellFile(document)
            if(result.code != "00000" and result.code != "50005"):
                log.error(f"File not downloaded Error. Error {result.code}: {result.consolLog}. Document: {document.id}")
                return result
            else:
                # Success
                document.status = document.DOWNLOADED
                document.save()
        documentLocation = document.file.file_location
        fileName = document.file.file_name + document.file.file_ext
        documentPath = document.file.file_location + document.file.file_name + document.file.file_ext
        tempFolder = document.file.file_location

        # Copy to temp folder
        result = fileModule.copyToTemp(documentPath, tempFolder, fileName)
        if result.code != "00000":
            return result

        # Images Folder
        imageFolder = tempFolder + 'images/'
        result = fileModule.makeDirectory(imageFolder, False)
        if result.code != "00000":
            return result

        documentPath = settings.MEDIA_ROOT + documentPath
        imagePath = settings.MEDIA_ROOT + imageFolder

        # PARSE TIF FILES
        if ext == "tiff" or ext == ".tif":
            log.debug('Processing TIF file.')
            success = True

            # Get number of pages
            try:
                img = Image.open(documentPath)
                width, height = img.size
                pixels = width*height
                log.debug('Pixels: %i, Document: %i', pixels, document.id)
                log.debug('Max Pixels %i', Image.MAX_IMAGE_PIXELS)

                img.load()
                log.debug('Pages in TIFF file: %i', img.n_frames)
                pageCount = img.n_frames
            except:
                result = GenerateResult(resultList,10)
                log.error(f"Error {result.code}: {result.consolLog}. Unable to load image. Document: {document.id}")

            # set quality
            if pageCount == 1 and pixels > 4000000:
                # Single page log file.
                document.conversion_status = document.IGNORED
                document.save()
                result = GenerateResult(resultList,0)
                return result
            else: 
                quality = 70

            try:
                #open tif
                im = Image.open(documentPath)
                success = True

                #loop through pages
                min = 0
                max = 1000
                if firstPage is not None:
                    min = firstPage - 1
                if lastPage is not None:
                    max = lastPage
                    if max > pageCount:
                        max = pageCount
                    max = max
                else:
                    max = pageCount

                # image folder
                imageLocation = document.file.file_location + document.file.file_name + "/"
                x = imageLocation.find("/")
                imageLocation = "file_images" + imageLocation[x:]
                result = fileModule.makeDirectory(imageLocation, settings.USE_S3)

                for i in range(min,max):
                    if(i == 999):
                        result = GenerateResult(resultList,13)
                        return result
                    try:
                        #load page
                        log.debug('Loading page %i', (i+1))
                        im.seek(i)
                        filePath = imagePath + '/page' + str(i+1) + '.jpg'
                        try:
                            im.thumbnail(im.size)
                            im.save(filePath, "JPEG", subsampling=0, quality=quality)
                        except:
                            result = GenerateResult(resultList,11)
                            result.consolLog =  result.consolLog + ". Failed to create JPEG: " + filePath
                            log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i+1)}")
                            success = False

                        try:
                            fileSize = os.path.getsize(filePath)
                        except Exception as e:
                            if hasattr(e, 'message'):
                                # Handle Error
                                result = GenerateResult(resultList,11)
                                result.consolLog = result.consolLog + ". Message: " + e.message
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i)}")
                                success = False
                            else:
                                # Handle Error
                                result = GenerateResult(resultList,11)
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i)}")
                                success = False
                        
                        # Copy to permanent location
                        fileModule.uploadFileS3(filePath, imageLocation + 'page' + str(i+1) + ".jpg")
                        fileModule.deleteFile(imageFolder + 'page' + str(i+1) + ".jpg",False)
                        
                        # Create page object
                        oPage = Page.objects.filter(document=document, page_no=i+1).first()
                        if oPage is None:
                            log.debug('Creating new page for document: %s (%i) of well: %s)', document.document_name, document.id, document.well.well_name)
                            log.debug('file_name: page%s', (i+1))
                            log.debug('file_ext: .jpg')
                            log.debug('file_location: %s', imageLocation)
                            log.debug('file_size: %i', fileSize)
                            try:
                                file = File.objects.filter(
                                    file_name = 'page' + str(i+1),
                                    file_ext =  ".jpg",
                                    file_location = imageLocation,
                                    file_size = fileSize
                                ).first()
                                if file is None:
                                    file = File.objects.create(
                                        file_name = 'page' + str(i+1),
                                        file_ext =  ".jpg",
                                        file_location = imageLocation,
                                        file_size = fileSize
                                    )
                                oPage = Page.objects.create(
                                    document = document,
                                    page_no = i+1,
                                    file = file,
                                    extracted = False
                                )
                            except Exception as e:
                                result = GenerateResult(resultList,5)
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i+1)}")
                                success = False
                        else:
                            try:
                                file = oPage.file
                                if file:    
                                    file.file_name = 'page' + str(i+1)
                                    file.file_ext =  ".jpg"
                                    file.file_location = imageLocation
                                    file.file_size = fileSize

                                    file.save()  
                                else:
                                    file = File.objects.filter(
                                        file_name = 'page' + str(i+1),
                                        file_ext =  ".jpg",
                                        file_location = imageLocation,
                                        file_size = fileSize
                                    ).first()
                                    if file is None:
                                        file = File.objects.create(
                                            file_name = 'page' + str(i+1),
                                            file_ext =  ".jpg",
                                            file_location = imageLocation,
                                            file_size = fileSize
                                        )
                                    oPage.file = file
                                    oPage.save()

                            except Exception as e:
                                result = GenerateResult(resultList,6)
                                print(e)
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i+1)}")
                                success = False
                    except EOFError:
                        if hasattr(e, 'message'):
                            # Not enough frames in img
                            result = GenerateResult(resultList,10)
                            result.consolLog =  result.consolLog + ". Message: " + e.message
                            log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i+1)}")
                            success = False
                            break
                        else:
                            # Not enough frames in img
                            result = GenerateResult(resultList,10)
                            result.consolLog =  result.consolLog + "Not enough frames in img."
                            log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(i+1)}")
                            success = False
                            break
                        
            
            except Exception as e:
                result = GenerateResult(resultList,10)
                result.consolLog =  result.consolLog + ". Failed to open: " + imagePath + ". Image is probably too large."
                log.error(f"Error {result.code}: {result.consolLog} Document: {document.id}, Page: {(i+1)}")
                return result
            
            if(success):
                if firstPage == 1 and pageCount == max:
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
                    print(e)
                    if hasattr(e, 'message'):
                        # Handle Error
                        result = GenerateResult(resultList,14)
                        result.consolLog = result.consolLog + ". Message: " + e.message
                        log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}")
                        return result
                    else:
                        # Handle Error
                        result = GenerateResult(resultList,14)
                        log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}")
                        return result

                if(success):
                    # image folder
                    imageLocation = document.file.file_location + document.file.file_name + "/"
                    x = imageLocation.find("/")
                    imageLocation = "file_images" + imageLocation[x:]
                    result = fileModule.makeDirectory(imageLocation, settings.USE_S3)

                    # save pages
                    for i, page in enumerate(pages):
                        pageNo = i + firstPage
                        filePath = imagePath + 'page' + str(pageNo) + ".jpg"
                        page.save(filePath, 'JPEG')

                        try:
                            fileSize = os.path.getsize(imagePath)
                        except Exception as e:
                            if hasattr(e, 'message'):
                                # Handle Error
                                result = GenerateResult(resultList,11)
                                result.consolLog = result.consolLog + ". Message: " + e.message
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(pageNo)}")
                                success = False
                            else:
                                # Handle Error
                                result = GenerateResult(resultList,11)
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(pageNo)}")
                                success = False

                        # Copy to permanent location
                        fileModule.uploadFileS3(filePath, imageLocation + 'page' + str(pageNo) + ".jpg")
                        fileModule.deleteFile(imageFolder + 'page' + str(pageNo) + ".jpg",False)

                        # Create page object
                        oPage = Page.objects.filter(document=document, page_no=pageNo).first()
                        if oPage is None:
                            try:
                                file = File.objects.filter(
                                    file_name = 'page' + str(pageNo),
                                    file_ext =  ".jpg",
                                    file_location = imageLocation,
                                    file_size = fileSize
                                ).first()
                                print(file)
                                if file is None:
                                    file = File.objects.create(
                                        file_name = 'page' + str(pageNo),
                                        file_ext =  ".jpg",
                                        file_location = imageLocation,
                                        file_size = fileSize
                                    )
                                oPage = Page.objects.create(
                                    document = document,
                                    page_no = pageNo,
                                    file = file,
                                    extracted = False
                                )
                            except Exception as e:
                                result = GenerateResult(resultList,5)
                                print(e)
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(pageNo)}")
                                success = False
                        else:
                            try:
                                file = oPage.file
                                if file:    
                                    file.file_name = 'page' + str(pageNo)
                                    file.file_ext =  ".jpg"
                                    file.file_location = imageLocation
                                    file.file_size = fileSize

                                    file.save()  
                                else:
                                    file = File.objects.filter(
                                        file_name = 'page' + str(pageNo),
                                        file_ext =  ".jpg",
                                        file_location = imageLocation,
                                        file_size = fileSize
                                    ).first()
                                    if file is None:
                                        file = File.objects.create(
                                            file_name = 'page' + str(pageNo),
                                            file_ext =  ".jpg",
                                            file_location = imageLocation,
                                            file_size = fileSize
                                        )
                                    oPage.file = file
                                    oPage.save()

                            except Exception as e:
                                result = GenerateResult(resultList,6)
                                log.error(f"Error {result.code}: {result.consolLog}. Document: {document.id}, Page: {(pageNo)}")
                                success = False              

                if(success):
                    if firstPage == 1 and i < lastPage:
                        document.conversion_status = document.CONVERTED
                        document.save()        

    else:
        document.conversion_status = document.IGNORED
        document.save()   
        success = True     

    if success:
        result = GenerateResult(resultList,0)
        return result
    else:
        result = GenerateResult(resultList,8)
        return result
    
def getDocumentText(document):
    pages = Page.objects.filter(document = document, extracted = False).all()

    for page in pages:
        if not page.extracted:
            file = page.file
            if file:
                fileName = file.file_name + file.file_ext
                filePath = file.file_location + file.file_name + file.file_ext
                tempFolder = file.file_location

                # Copy to temp folder
                result = fileModule.copyToTemp(filePath, tempFolder, fileName)
                if result.code != "00000":
                    return result

                path = file.path()

                result = getTextArray(path)
                if result.code != "00000":
                    return result

                pageTexts = result.texts

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
        result = GenerateResult(resultList,9)
        result.consolLog = result.consolLog + ". " + response.error.message + '\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors'
        return result

    result = GenerateResult(resultList,0)
    result.texts = texts
    return result

def ExtractData(document,method):
    pages = document.pages.all()
    actions = method.actions.all()
    log.debug("*****************************************************")
    log.debug("Extracting Data from Document: %s (%i), using method: %s (%i)", document.document_name, document.id, method.name, method.id)
    
    for page in pages:
        if page.page_no != 2:
            continue
        log.debug("Page %i", page.page_no)
        texts = page.texts.all()
        for text in texts:
            actionResults = []
            columns = []
            rows = []
    
            partialSuccess = False
            for i, a in enumerate(actions):
                action = a.action
                # Initial Action
                if action.type == action.INITIAL:
                    actionResult = InitialAction(text,action)

                # Next Action
                elif action.type == action.NEXT:
                    try:
                        previousAction = actionResults[action.start-1]
                    except:
                        log.error(f"Start action out of range. Method {method.id}, Action: {action.id}")
                        break

                    previousText = previousAction.texts[-1].text

                    # Check if it was on the end of the previous action
                    success = False
                    chkStr = strCorrections(action.string, action.remove_chars, True)
                    if previousText:
                        if len(previousText) > len(chkStr):
                            if previousText[-1*len(chkStr):] == chkStr:
                                success = True

                                # adjust previous text
                                endCut = -1*len(chkStr)
                                previousText = previousText[:endCut]

                                # save results
                                actionResults[action.start-1].text = previousText
                                actionResult = Action(previousAction.texts,chkStr,True,action)
                    if not success:
                        actionResult = NextAction(action, actionResults[action.start-1], actionResults[action.lower_bound_start-1], actionResults[action.upper_bound_start-1], page)

                # Search Action
                #if action.type == action.SEARCH:
                    #actionResult = SearchAction(action, actionResults[action.start-1], page)
                
                # Value Action
                elif action.type == action.VALUE:
                    actionResult = ValueAction(action, actionResults[action.start-1], actionResults[action.lower_bound_start-1], actionResults[action.upper_bound_start-1], page)
                    if actionResult.success:
                        valueText = actionResult.text

                        if valueText is not None:
                            if not IsNumber(valueText):
                                if len(actions) > i + 1:
                                    nextAction = actions[i+1].action
                                    if nextAction.start == i+1:
                                        if nextAction.string is not None:
                                            chkStr = strCorrections(nextAction.string, action.remove_chars, True)
                                            if valueText[-1*len(chkStr):] == chkStr:
                                                endCut = -1*len(chkStr)
                                                valueText = valueText[:endCut]

                                if len(valueText) > 4:
                                    if valueText[-3] == ',':
                                        valueText = valueText[:-3] + '.' + valueText[-2:]

                            if IsNumber(valueText):
                                try:
                                    value = Decimal(valueText)
                                    actionResult.value = value
                                except Exception as e:
                                    actionResult = Action(actionResult.texts,actionResult.text, False, action)
                            else:
                                actionResult = Action(actionResult.texts,actionResult.text, False, action)
                        else:
                            actionResult = Action(actionResult.texts,actionResult.text, False, action)


                # Text Value Action
                elif action.type == action.TEXTVALUE:
                    actionResult = ValueAction(action, actionResults[action.start-1], actionResults[action.lower_bound_start-1], actionResults[action.upper_bound_start-1], page)

                # Save Action
                elif action.type == action.SAVE:
                    actionResult = Action(None,None, True, action)
                    partialSuccess = True

                # Next Data Row
                elif action.type == action.NEXTDATA:
                    actionResult = Action(None,None, True, action)



                # Table Header
                elif action.type == action.TABLEHEADER:
                    actionResult = TableHeader(action, actionResults[0], page)

                # Table Rows
                elif action.type == action.TABLEROW:
                    # Get columns
                    for result in actionResults:
                        ra = result.action
                        if ra.type == action.TABLEHEADER or result.tableHeader:
                            col = Column(ra.startUpper, result.colMin, result.colMax, result.yMin, result.yMax)
                            columns.append(col)

                    columns.sort(key=lambda x: x.no)

                    # fix column boundaries
                    ymin = 9999999999
                    ymax = 0
                    percent = actionResults[0].action.offset_percent
                    if percent is None:
                        percent = 0
                    pixels = actionResults[0].action.offset_pixels
                    if pixels is None:
                        pixels = 0

                    for i in range(len(columns)-1):
                        if i != 0:
                            x = (columns[i-1].xmax + columns[i].xmin)/2
                            columns[i-1].xmax = x
                            columns[i].xmin = x

                        if columns[i].ymin < ymin:
                            ymin = columns[i].ymin

                        if columns[i].ymax > ymax:
                            ymax = columns[i].ymax

                    ymax = ymax + (ymax - ymin)/2 * percent/100 + pixels

                    for column in columns:
                        column.ymin = ymin
                        column.ymax = ymax
                        print(f"Column {column.no} ({column.xmin}, {column.xmax})")

                    rows = TableRows(action, columns, page)
                    for i, row in enumerate(rows):
                        print(f"Row {i+1} ({row.ymin}, {row.ymax})")
                    
                    actionResult = Action(None, None, True,action)
                
                # Table Cells
                elif action.type == action.TABLECELLVALUE or action.type == action.TABLECELLTEXT:
                    if columns and rows:
                        col = None
                        for column in columns:
                            if column.no == action.start:
                                col = column
                        if col:
                            for row in rows:
                                actionResult = TableCell(action, col.xmin, col.xmax, row.ymin, row.ymax, page)
                                if actionResult.success:
                                    if action.type == action.TABLECELLVALUE:
                                        try:
                                            value = Decimal(actionResult.text)
                                            row.values.append(value)
                                            row.units.append(action.unit)
                                        except Exception as e:
                                            log.error(e)
                                            row.values.append(None)
                                            row.units.append(action.unit)
                                    else:
                                        row.values.append(actionResult.text)
                                        row.units.append(action.unit)
                                else:
                                    row.values.append(None)
                                    row.units.append(action.unit)
                        else:
                            actionResult = Action(None, None, True,action)
                    else:                    
                        actionResult = Action(None, None, True,action)

                # No action type
                else:
                    actionResult = Action(None,None,False,action)

                if not actionResult.success:
                    if action.type != action.INITIAL:
                        #pass
                        log.debug(actionResult)
                    if actionResult.action.can_fail:
                        actionResult.value=None
                        actionResults.append(actionResult)
                    else:
                        break
                else:
                    log.debug(actionResult)
                    actionResults.append(actionResult)

                
                
            # Check Success
            if len(actions) != 0 and len(actions) == len(actionResults) or partialSuccess:
                log.debug("SUCCESS Extracting Data from Document: %s (%i), using method: %s (%i)", document.document_name, document.id, method.name, method.id)

                # Save Table
                if actionResults[0].action.startUpper:
                    for row in rows:
                        fvalues = [None, None, None, None]
                        ftexts = [None, None, None, None]
                        funits = [None, None, None, None]
                        for i in range(len(row.values)):
                            if row.units[i]:
                                if row.units[i].name == 'text':
                                    ftexts[i] = row.values[i]                                
                                else:
                                    fvalues[i] = row.values[i]
                            funits[i] = row.units[i]

                        print("***********************************************")
                        print(fvalues)
                        print(ftexts)
                        print(funits)
                        # check no all null
                        chk = False
                        for v in fvalues:
                            if v:
                                chk = True
                        for t in ftexts:
                            if t:
                                chk = True
                        
                        if chk:
                            data = Data.objects.filter(
                                page = page,
                                extraction_method__data_type = method.data_type,
                                value = fvalues[0],
                                text = ftexts[0],
                                unit = funits[0],
                                value2 = fvalues[1],
                                text2 = ftexts[1],
                                unit2 = funits[1],
                                value3 = fvalues[2],
                                text3 = ftexts[2],
                                unit3 = funits[2],
                                value4 = fvalues[3],
                                text4 = ftexts[3],
                                unit4 = funits[3]
                            ).first()
                            if data is None:
                                try:
                                    data = Data.objects.create(
                                        page = page,
                                        extraction_method = method,
                                        value = fvalues[0],
                                        text = ftexts[0],
                                        unit = funits[0],
                                        value2 = fvalues[1],
                                        text2 = ftexts[1],
                                        unit2 = funits[1],
                                        value3 = fvalues[2],
                                        text3 = ftexts[2],
                                        unit3 = funits[2],
                                        value4 = fvalues[3],
                                        text4 = ftexts[3],
                                        unit4 = funits[3]
                                    )
                                except Exception as e:
                                    print(e)
                                    success = False

                # Get Values
                values = []
                texts = []
                units = []
                success = True
                j = 0
                k = 0
                for i in range(len(actionResults)):
                    action = actions[i].action
                    actionResult = actionResults[i]

                    # VALUES
                    if action.type == action.VALUE:
                        value = actionResult.value
                            
                        values.append(value)
                        texts.append(None)
                        units.append(action.unit)
                        k += 1
                        
                    # TEXT
                    if action.type == action.TEXTVALUE:
                        valueText = actionResult.text
                        unit = Unit.objects.filter(name="text").first()
                    
                        values.append(0)
                        texts.append(valueText)
                        units.append(unit)
                        k += 1

                    # SAVE ROW
                    if action.type == action.SAVE:
                        fvalues = [None, None, None, None]
                        ftexts = [None, None, None, None]
                        funits = [None, None, None, None]
                        print("#SAVING VALUES ####################") 
                        for i in range(len(values)-j):
                            if values[i+j]:
                                fvalues[i] = Decimal(round(values[i+j],2))
                            ftexts[i] = texts[i+j]
                            funits[i] = units[i+j]
                        print(fvalues)

                        data = Data.objects.filter(
                            page = page,
                            extraction_method__data_type = method.data_type,
                            value = fvalues[0],
                            text = ftexts[0],
                            unit = funits[0],
                            value2 = fvalues[1],
                            text2 = ftexts[1],
                            unit2 = funits[1],
                            value3 = fvalues[2],
                            text3 = ftexts[2],
                            unit3 = funits[2],
                            value4 = fvalues[3],
                            text4 = ftexts[3],
                            unit4 = funits[3]
                        ).first()

                        if data is None:
                            try:
                                data = Data.objects.create(
                                    page = page,
                                    extraction_method = method,
                                    value = fvalues[0],
                                    text = ftexts[0],
                                    unit = funits[0],
                                    value2 = fvalues[1],
                                    text2 = ftexts[1],
                                    unit2 = funits[1],
                                    value3 = fvalues[2],
                                    text3 = ftexts[2],
                                    unit3 = funits[2],
                                    value4 = fvalues[3],
                                    text4 = ftexts[3],
                                    unit4 = funits[3]
                                )
                            except Exception as e:
                                print(e)
                                success = False
                        j = k

                # SAVE LAST ROW
                if success and not partialSuccess:  
                    fvalues = [None, None, None, None]
                    ftexts = [None, None, None, None]
                    funits = [None, None, None, None]
                    print("SAVING VALUES ####################") 
                    for i in range(len(values)-j):
                        fvalues[i] = values[i+j]
                        ftexts[i] = texts[i+j]
                        funits[i] = units[i+j]
                    print(fvalues)

                    data = Data.objects.filter(
                        page = page,
                        extraction_method__data_type = method.data_type,
                        value = fvalues[0],
                        text = ftexts[0],
                        unit = funits[0],
                        value2 = fvalues[1],
                        text2 = ftexts[1],
                        unit2 = funits[1],
                        value3 = fvalues[2],
                        text3 = ftexts[2],
                        unit3 = funits[2],
                        value4 = fvalues[3],
                        text4 = ftexts[3],
                        unit4 = funits[3]
                        ).first()
                    if data is None:
                        try:
                            data = Data.objects.create(
                                page = page,
                                extraction_method = method,
                                value = fvalues[0],
                                text = ftexts[0],
                                unit = funits[0],
                                value2 = fvalues[1],
                                text2 = ftexts[1],
                                unit2 = funits[1],
                                value3 = fvalues[2],
                                text3 = ftexts[2],
                                unit3 = funits[2],
                                value4 = fvalues[3],
                                text4 = ftexts[3],
                                unit4 = funits[3]
                            )
                        except Exception as e:
                            print(e)
            else:
                pass
                #log.debug("FAILED Extracting Data from Document: %s (%i), using method: %s (%i)", document.document_name, document.id, method.name, method.id)

    return True

def strCorrections(str, remove_chars, lower):
    if str is None:
        return None
    else:
        if remove_chars:
            ignoreList = remove_chars.split('#')
            for ignore in ignoreList:
                str = str.replace(ignore,"")

        if lower:
            str = str.lower()
        
        return str

def InitialAction(text,action):
    chkStr = strCorrections(action.string, action.remove_chars, True)
    foundStr = strCorrections(text.text, action.remove_chars, True)
    if (chkStr in foundStr):
        texts = []
        texts.append(text)
        result = Action(texts,foundStr,True,action)
        # If table header
        if action.startUpper:
            polyResult = processPoly(text)
            if polyResult.code == "00000":
                poly = polyResult.poly
                result.tableHeader = True

                xdif = poly['xdif']
                if action.lower_offset_percent:
                    lowerPercent = action.lower_offset_percent
                else:
                    lowerPercent = 0
                if action.lower_offset_pixels:
                    lowerPixels = action.lower_offset_pixels
                else:
                    lowerPixels = 0

                if action.upper_offset_percent:
                    upperPercent = action.upper_offset_percent
                else:
                    upperPercent = 0
                if action.upper_offset_pixels:
                    upperPixels = action.upper_offset_pixels
                else:
                    upperPixels = 0

                xmin = poly['x1'] - xdif * (lowerPercent/100) - lowerPixels
                xmax = poly['x2'] + xdif * (upperPercent/100) + upperPixels

                result.colMin = xmin
                result.colMax = xmax
                result.yMin = poly['y1']
                result.yMax = poly['y2']
        
        log.debug("Initial Action: %s", foundStr)
    else:
        result = Action(None,None,False,action)
    
    return result

def NextAction(action, startAction, startActionLower, startActionUpper, page):
    if action.string == "#":
        chkStr = "#"
    else:
        chkStr = strCorrections(action.string, action.remove_chars, True) 
    if action.remove_chars:
        ignoreList = action.remove_chars.split('#')
    else:
        ignoreList = None

    # Starting Text
    # Right or Down
    if(action.direction == action.RIGHT or action.direction == action.DOWN):
        startText = startAction.texts[-1]
        startTextLower = startActionLower.texts[-1]
        startTextUpper = startActionUpper.texts[-1]
    # Left or Up
    if(action.direction == action.LEFT or action.direction == action.UP):
        startText = startAction.texts[0]
        startTextLower = startActionLower.texts[0]
        startTextUpper = startActionUpper.texts[0]

    foundStr = ""
    aTexts = []

    for i in range(10):
        result = processPoly(startText)
        if result.code != "00000":
            result.text = None
            return result
        else:
            poly = result.poly

        result = processPoly(startTextLower)
        if result.code != "00000":
            result.text = None
            return result
        else:
            polyLower = result.poly

        result = processPoly(startTextUpper)
        if result.code != "00000":
            result.text = None
            return result
        else:
            polyUpper = result.poly


        texts = Text.objects.filter(
            page = page)
        
        # Offsets
        if action.offset_percent:
            percent = action.offset_percent
        else:
            percent = 0
        
        if action.offset_pixels:
            pixels = action.offset_pixels
        else:
            pixels = 0

        # Right 
        if(action.direction == action.RIGHT):
            start = poly['x2']+poly['xdif']*(percent/100)+pixels
            texts = texts.filter(BoundingPolys__x__gte = start)
            
            lowerBound = polyLower['y1']-polyLower['ydif']*(action.lower_offset_percent/100)-action.lower_offset_pixels
            texts = texts.filter(BoundingPolys__y__gte = lowerBound)

            if action.upper_bound==action.START:
                upperBound = polyUpper['y2']+polyUpper['ydif']*(action.upper_offset_percent/100)+action.upper_offset_pixels
            if action.upper_bound==action.MID:
                upperBound = (polyUpper['y2']+polyUpper['y2'])/2+polyUpper['ydif']*(action.upper_offset_percent/100)+action.upper_offset_pixels
            if action.upper_bound==action.END:
                upperBound = polyUpper['y1']+polyUpper['ydif']*(action.upper_offset_percent/100)+action.upper_offset_pixels
            texts = texts.filter(BoundingPolys__y__lte = upperBound)

            x = 9999999
        # LEFT
        elif(action.direction == action.LEFT):
            start = poly['x1']-poly['xdif']*(percent/100)-pixels
            texts = texts.filter(BoundingPolys__x__lte = start)

            lowerBound = polyLower['y1']-polyLower['ydif']*(action.lower_offset_percent/100)-action.lower_offset_pixels
            texts = texts.filter(BoundingPolys__y__gte = lowerBound)

            upperBound = polyUpper['y2']+polyUpper['ydif']*(action.upper_offset_percent/100)+action.upper_offset_pixels
            texts = texts.filter(BoundingPolys__y__lte = upperBound)

            x = -9999999
        # Up
        elif(action.direction == action.UP):
            start = poly['y1']-poly['ydif']*(percent/100)-pixels
            texts = texts.filter(BoundingPolys__y__lte = start)

            lowerBound = polyLower['x1']-polyLower['xdif']*(action.lower_offset_percent/100)-action.lower_offset_pixels
            texts = texts.filter(BoundingPolys__x__gte = lowerBound)

            upperBound = polyUpper['x2']+polyUpper['xdif']*(action.upper_offset_percent/100)+action.upper_offset_pixels
            texts = texts.filter(BoundingPolys__x__lte = upperBound)

            y = -9999999
        # Down
        elif(action.direction == action.DOWN):
            start = poly['y2']+poly['ydif']*(percent/100)+pixels
            texts = texts.filter(BoundingPolys__y__gte = start)

            lowerBound = polyLower['x1']-polyLower['xdif']*(action.lower_offset_percent/100)-action.lower_offset_pixels
            texts = texts.filter(BoundingPolys__x__gte = lowerBound)

            upperBound = polyUpper['x2']+polyUpper['xdif']*(action.upper_offset_percent/100)+action.upper_offset_pixels
            texts = texts.filter(BoundingPolys__x__lte = upperBound)

            y = 9999999
        
        # Ignore List
        if ignoreList:
            for ignore in ignoreList:
                texts = texts.exclude(text=ignore)
        
        # Distinct
        texts = texts.distinct()
        #log.debug(f"x start: {start}")
        #log.debug(f"lowerBound: {lowerBound}")
        #log.debug(f"upperBound: {upperBound}")  
        
        fText = None        

        for t in texts:
            if t != startText:
                result = processPoly(t)
                if result.code == "00000":
                    testPoly = result.poly
                    #log.debug(f"{t.text} ({testPoly['xave']},{testPoly['yave']})")

                    if(action.direction == action.RIGHT):
                        if testPoly['xave'] > poly['x2'] and testPoly['xave'] < x:
                            if testPoly['yave'] > lowerBound and testPoly['yave'] < upperBound:
                                x = testPoly['xave']
                                fText = t
                    elif(action.direction == action.LEFT):
                        if testPoly['xave'] < poly['x2'] and testPoly['xave'] > x:
                            if testPoly['yave'] > lowerBound and testPoly['yave'] < upperBound:
                                x = testPoly['xave']
                                fText = t

                    elif(action.direction == action.UP):
                        if testPoly['yave'] < poly['y2'] and testPoly['yave'] > (y+4):
                            if testPoly['xave'] > lowerBound and testPoly['xave'] < upperBound:
                                y = testPoly['yave']
                                fText = t

                    elif(action.direction == action.DOWN):
                        if testPoly['yave'] > poly['y2'] and testPoly['yave'] < y:
                            if testPoly['xave'] > lowerBound and testPoly['xave'] < upperBound:
                                y = testPoly['yave']
                                fText = t



        if fText is not None:
            aTexts.append(fText)
            if chkStr == "#":
                result = Action(aTexts,foundStr,True,action)
                log.debug("Next String (%s): %s", chkStr, foundStr)
                return result
            
            foundStr += strCorrections(fText.text, action.remove_chars, True)
            aTexts.append(fText)
            startText = fText

            #print(foundStr)

            if foundStr == chkStr:
                result = Action(aTexts,foundStr,True,action)
                log.debug("Next String (%s): %s", chkStr, foundStr)
                return result
            else:
                if not chkStr[:len(foundStr)] == foundStr:
                    log.debug("Next String - FAILED (%s): %s", chkStr, foundStr)
                    result = Action(aTexts,foundStr,False,action)
                    return result
                else:
                    log.debug("Next String - CONTINUE (%s): %s", chkStr, foundStr)
        else:
            log.debug("Next String - FAILED (%s): NULL", chkStr)
            result = Action(aTexts,foundStr,False,action)
            return result

    result = Action(None,None,False,action)
    return result

def SearchAction():
    pass

def ValueAction(action, startAction, startActionLower, startActionUpper, page):
    if startAction.texts is None:
        result = Action(None,None,False,action)
        return result
    if action.remove_chars:
        ignoreList = action.remove_chars.split('#')
    else:
        ignoreList = None

    # Right
    if(action.direction == action.RIGHT):
        # Right
        if startAction.action.direction == action.RIGHT:
            startText = startAction.texts[-1]
        # Left
        elif startAction.action.direction == action.LEFT:
            startText = startAction.texts[0]
        # Up
        elif startAction.action.direction == action.UP:
            startText = startAction.texts[-1]
        # Down
        else:
            startText = startAction.texts[0]

        # Lower Bound
        # Right
        if startActionLower.action.direction == action.RIGHT:
            lowerBoundText = startActionLower.texts[-1]
        # Left
        elif startActionLower.action.direction == action.LEFT:
            lowerBoundText = startActionLower.texts[0]
        # Up
        elif startActionLower.action.direction == action.UP:
            lowerBoundText = startActionLower.texts[-1]
        # Down
        else:
            lowerBoundText = startActionLower.texts[0]

        # Upper Bound
        # Right
        if startActionUpper.action.direction == action.RIGHT:
            upperBoundText = startActionUpper.texts[-1]
        # Left
        elif startActionUpper.action.direction == action.LEFT:
            upperBoundText = startActionUpper.texts[0]
        # Up
        elif startActionUpper.action.direction == action.UP:
            upperBoundText = startActionUpper.texts[0]
        # Down
        else:
            upperBoundText = startActionUpper.texts[-1]

    # Left
    if(action.direction == action.LEFT):
        # Right
        if startAction.action.direction == action.RIGHT:
            startText = startAction.texts[0]
        # Left
        elif startAction.action.direction == action.LEFT:
            startText = startAction.texts[-1]
        # Up
        elif startAction.action.direction == action.UP:
            startText = startAction.texts[-1]
        # Down
        else:
            startText = startAction.texts[0]

        # Lower Bound
        # Right
        if startActionLower.action.direction == action.RIGHT:
            lowerBoundText = startActionLower.texts[0]
        # Left
        elif startActionLower.action.direction == action.LEFT:
            lowerBoundText = startActionLower.texts[-1]
        # Up
        elif startActionLower.action.direction == action.UP:
            lowerBoundText = startActionLower.texts[-1]
        # Down
        else:
            lowerBoundText = startActionLower.texts[0]

        # Upper Bound
        # Right
        if startActionUpper.action.direction == action.RIGHT:
            upperBoundText = startActionUpper.texts[0]
        # Left
        elif startActionUpper.action.direction == action.LEFT:
            upperBoundText = startActionUpper.texts[-1]
        # Up
        elif startActionUpper.action.direction == action.UP:
            upperBoundText = startActionUpper.texts[0]
        # Down
        else:
            upperBoundText = startActionUpper.texts[-1]

    # Up
    if(action.direction == action.UP):
        # Right
        if startAction.action.direction == action.RIGHT:
            startText = startAction.texts[0]
        # Left
        elif startAction.action.direction == action.LEFT:
            startText = startAction.texts[-1]
        # Up
        elif startAction.action.direction == action.UP:
            startText = startAction.texts[-1]
        # Down
        else:
            startText = startAction.texts[0]

        # Lower Bound
        # Right
        if startActionLower.action.direction == action.RIGHT:
            lowerBoundText = startActionLower.texts[0]
        # Left
        elif startActionLower.action.direction == action.LEFT:
            lowerBoundText = startActionLower.texts[-1]
        # Up
        elif startActionLower.action.direction == action.UP:
            lowerBoundText = startActionLower.texts[-1]
        # Down
        else:
            lowerBoundText = startActionLower.texts[0]

        # Upper Bound
        # Right
        if startActionUpper.action.direction == action.RIGHT:
            upperBoundText = startActionUpper.texts[-1]
        # Left
        elif startActionUpper.action.direction == action.LEFT:
            upperBoundText = startActionUpper.texts[0]
        # Up
        elif startActionUpper.action.direction == action.UP:
            upperBoundText = startActionUpper.texts[-1]
        # Down
        else:
            upperBoundText = startActionUpper.texts[0]

    # Down
    if(action.direction == action.DOWN):
        # Right
        if startAction.action.direction == action.RIGHT:
            startText = startAction.texts[0]
        # Left
        elif startAction.action.direction == action.LEFT:
            startText = startAction.texts[-1]
        # Up
        elif startAction.action.direction == action.UP:
            startText = startAction.texts[0]
        # Down
        else:
            startText = startAction.texts[-1]

        # Lower Bound
        # Right
        if startActionLower.action.direction == action.RIGHT:
            lowerBoundText = startActionLower.texts[0]
        # Left
        elif startActionLower.action.direction == action.LEFT:
            lowerBoundText = startActionLower.texts[-1]
        # Up
        elif startActionLower.action.direction == action.UP:
            lowerBoundText = startActionLower.texts[0]
        # Down
        else:
            lowerBoundText = startActionLower.texts[-1]
        
        # Upper Bound
        # Right
        if startActionUpper.action.direction == action.RIGHT:
            upperBoundText = startActionUpper.texts[-1]
        # Left
        elif startActionUpper.action.direction == action.LEFT:
            upperBoundText = startActionUpper.texts[0]
        # Up
        elif startActionUpper.action.direction == action.UP:
            upperBoundText = startActionUpper.texts[0]
        # Down
        else:
            upperBoundText = startActionUpper.texts[-1]

    # startPoly
    result = processPoly(startText)
    if result.code != "00000":
        result.text = None
        return result
    else:
        startPoly = result.poly

    # poly1
    result = processPoly(lowerBoundText)
    if result.code != "00000":
        result.text = None
        return result
    else:
        poly1 = result.poly

    # poly2
    result = processPoly(upperBoundText)
    if result.code != "00000":
        result.text = None
        return result
    else:
        poly2 = result.poly

    # Combined Poly
    result = combinePolys(poly1, poly2)
    if result.code != "00000":
        result.text = None
        return result
    else:
        poly = result.poly

    texts = Text.objects.filter(
        page = page)
    
    # Offsets
    if action.offset_percent:
        percent = action.offset_percent
    else:
        percent = 0
    
    if action.offset_pixels:
        pixel = action.offset_pixels
    else:
        pixel = 0

    if action.lower_offset_percent:
        lPercent = action.lower_offset_percent
    else:
        lPercent = 0
    
    if action.upper_offset_percent:
        hPercent = action.upper_offset_percent
    else:
        hPercent = 0

    if action.lower_offset_pixels:
        lPixel = action.lower_offset_pixels
    else:
        lPixel = 0

    if action.upper_offset_pixels:
        hPixel = action.upper_offset_pixels
    else:
        hPixel = 0

    # Right 
    if(action.direction == action.RIGHT):
        start = startPoly['x2'] + startPoly['xdif']*(percent/100) + pixel
        texts = texts.filter(BoundingPolys__x__gte = start)
        
        # Lower Bound
        if action.lower_bound == action.START:
            lowerStart = poly['y1']
        elif action.lower_bound == action.MID:
            lowerStart = poly['y1']+poly['ydif']/2
        else:
            lowerStart = poly['y2']

        lowerBound = lowerStart - poly['ydif']*(lPercent/100) - lPixel
        texts = texts.filter(BoundingPolys__y__gte = lowerBound)
        
        # Upper Bound
        if action.lower_bound == action.START:
            upperStart = poly['y2']
        elif action.lower_bound == action.MID:
            upperStart = poly['y2']-poly['ydif']/2
        else:
            upperStart = poly['y1']
            
        upperBound = upperStart + poly['ydif']*(hPercent/100) + hPixel
        texts = texts.filter(BoundingPolys__y__lte = upperBound)

        x = 9999999
    # LEFT
    elif(action.direction == action.LEFT):
        start = startPoly['x1'] - startPoly['xdif']*(percent/100) - pixel
        texts = texts.filter(BoundingPolys__x__lte = start)

        # Lower Bound
        if action.lower_bound == action.START:
            lowerStart = poly['y1']
        elif action.lower_bound == action.MID:
            lowerStart = poly['y1']+poly['ydif']/2
        else:
            lowerStart = poly['y2']

        lowerBound = lowerStart - poly['ydif']*(lPercent/100) - lPixel
        texts = texts.filter(BoundingPolys__y__gte = lowerBound)
        
        # Upper Bound
        if action.lower_bound == action.START:
            upperStart = poly['y2']
        elif action.lower_bound == action.MID:
            upperStart = poly['y2']-poly['ydif']/2
        else:
            upperStart = poly['y1']

        upperBound = upperStart + poly['ydif']*(hPercent/100) + hPixel
        texts = texts.filter(BoundingPolys__y__lte = upperBound)

        x = -9999999
    # Up
    elif(action.direction == action.UP):
        start = startPoly['y1'] - startPoly['ydif']*(percent/100) - pixel
        texts = texts.filter(BoundingPolys__y__lte = start)

        # Lower Bound
        if action.lower_bound == action.START:
            lowerStart = poly['x1']
        elif action.lower_bound == action.MID:
            lowerStart = poly['x1']+poly['xdif']/2
        else:
            lowerStart = poly['x2']

        lowerBound = lowerStart - poly['xdif']*(lPercent/100) - lPixel
        texts = texts.filter(BoundingPolys__x__gte = lowerBound)
        
        # Upper Bound
        if action.lower_bound == action.START:
            upperStart = poly['x2']
        elif action.lower_bound == action.MID:
            upperStart = poly['x2']-poly['xdif']/2
        else:
            upperStart = poly['x1']

        upperBound = upperStart + poly['xdif']*(hPercent/100) + hPixel
        texts = texts.filter(BoundingPolys__x__lte = upperBound)

        y = -9999999
        x = 9999999     
    # Down
    elif(action.direction == action.DOWN):
        start = startPoly['y2'] + startPoly['ydif']*(percent/100) + pixel
        texts = texts.filter(BoundingPolys__y__gte = start)

        # Lower Bound
        if action.lower_bound == action.START:
            lowerStart = poly['x1']
        elif action.lower_bound == action.MID:
            lowerStart = poly['x1']+poly['xdif']/2
        else:
            lowerStart = poly['x2']

        lowerBound = lowerStart - poly['xdif']*(lPercent/100) - lPixel
        texts = texts.filter(BoundingPolys__x__gte = lowerBound)
        
        # Upper Bound
        if action.lower_bound == action.START:
            upperStart = poly['x2']
        elif action.lower_bound == action.MID:
            upperStart = poly['x2']-poly['xdif']/2
        else:
            upperStart = poly['x1']

        upperBound = upperStart + poly['xdif']*(hPercent/100) + hPixel
        texts = texts.filter(BoundingPolys__x__lte = upperBound)

        y = 9999999
        x = 9999999
    
    # Ignore List
    if ignoreList:
        for ignore in ignoreList:
            texts = texts.exclude(text=ignore)
    
    # Distinct
    texts = texts.distinct()

    # Get first value
    fText = None
    for t in texts:
        #print(t.text)
        if t != startText and t != lowerBoundText and t != upperBoundText:
            result = processPoly(t)
            if result.code == "00000":
                testPoly = result.poly

                if(action.direction == action.RIGHT):
                    if testPoly['xave'] > poly['x2'] and testPoly['xave'] < x:
                        if testPoly['yave'] > lowerBound and testPoly['yave'] < upperBound:
                            x = testPoly['xave']
                            fText = t
                elif(action.direction == action.LEFT):
                    if testPoly['xave'] < poly['x2'] and testPoly['xave'] > x:
                        if testPoly['yave'] > lowerBound and testPoly['yave'] < upperBound:
                            x = testPoly['xave']
                            fText = t

                elif(action.direction == action.UP):
                    test = False
                    if testPoly['yave'] < poly['y2'] and testPoly['yave'] > (y - 4) and testPoly['xave'] < x:
                        test = True
                    elif testPoly['yave'] < poly['y2'] and testPoly['yave'] > (y + 4):
                        test = True
                    if test:
                        if testPoly['xave'] > lowerBound and testPoly['xave'] < upperBound:
                            y = testPoly['yave']
                            x = testPoly['xave']
                            fText = t

                elif(action.direction == action.DOWN):
                    test = False
                    if testPoly['yave'] > poly['y2'] and testPoly['yave'] < (y + 8) and testPoly['xave'] < x:
                        test = True
                    elif testPoly['yave'] > poly['y2'] and testPoly['yave'] < (y - 8):
                        test = True
                    if test:
                        if testPoly['xave'] > lowerBound and testPoly['xave'] < upperBound:
                            y = testPoly['yave']
                            x = testPoly['xave']
                            fText = t


    if fText is not None:
        foundStr = strCorrections(fText.text, action.remove_chars, False)
        log.debug("Get Value found string: %s", foundStr)
 
        aTexts = []
        aTexts.append(fText)

        # VALUE Only
        if action.type == action.VALUE:
            x = re.findall(r"\d+", foundStr)
            if len(x) == 1:
                foundStr = x[0]
            elif len(x) == 2:
                start = re.search(x[0], foundStr)
                end = re.search(x[1], foundStr)
                if end.start() - start.end() == 1:
                    decimalPointStr = foundStr[start.end():end.start()]
                    if decimalPointStr == ".":
                        foundStr = x[0] + "." + x[1]
                    else:
                        result = Action(aTexts,foundStr,False,action)
                        return result
                else:
                    foundStr=x[0]
            else:
                result = Action(aTexts,foundStr,False,action)
                return result

        # TEXTVALUE Only
        if action.type == action.TEXTVALUE:
            # Get rest of text string
            startText = fText
            # poly
            result = processPoly(startText)
            if result.code != "00000":
                result.text = None
                return result
            else:
                poly = result.poly
                
            texts = Text.objects.filter(
                page = page)
            texts = texts.filter(BoundingPolys__x__gte = poly['x2'])
        
            # Lower Bound
            lowerStart = poly['y1']
            lowerBound = lowerStart - 2
            texts = texts.filter(BoundingPolys__y__gte = lowerBound)
            
            # Upper Bound
            upperStart = poly['y2']
            upperBound = upperStart + 2
            texts = texts.filter(BoundingPolys__y__lte = upperBound)

            # Distinct
            texts = texts.distinct()
            for i in range(10):
                fText = None
                for t in texts:
                    if t != startText:
                        #print(t)
                        result = processPoly(t)
                        if result.code == "00000":
                            testPoly = result.poly

                            if testPoly['xave'] > poly['x2'] and testPoly['x1'] < (poly['x2']+20):
                                #print("test x")
                                if testPoly['yave'] > lowerBound and testPoly['yave'] < upperBound:
                                    #print("test y")
                                    fText = t



                if fText is not None:
                    foundStr += " " + strCorrections(fText.text, action.remove_chars, False)
                    aTexts.append(fText)
                    # poly
                    result = processPoly(fText)
                    if result.code != "00000":
                        result.text = None
                        return result
                    else:
                        poly = result.poly
                    
                    startText = fText

        result = Action(aTexts,foundStr,True,action)
        
        return result

    result = Action(None,None,False,action)
    return result

def TableHeader(action, referenceAction, page):
    foundStr = ""

    # Ignore List
    if action.remove_chars:
        ignoreList = action.remove_chars.split('#')
    else:
        ignoreList = None

    # Offsets
    if action.offset_percent:
        percent = action.offset_percent
    else:
        percent = 0
    if action.offset_pixels:
        pixels = action.offset_pixels
    else:
        pixels = 0

    if referenceAction.action.lower_offset_percent:
        xLowerPercent = referenceAction.action.lower_offset_percent
    else:
        xLowerPercent = 0
    if referenceAction.action.lower_offset_pixels:
        xLowerPixels = referenceAction.action.lower_offset_pixels
    else:
        xLowerPixels = 0

    if referenceAction.action.upper_offset_percent:
        xUpperPercent = referenceAction.action.upper_offset_percent
    else:
        xUpperPercent = 0
    if referenceAction.action.upper_offset_pixels:
        xUpperPixels = referenceAction.action.upper_offset_pixels
    else:
        xUpperPixels = 0

    # Head Row Bounds 
    result = processPoly(referenceAction.texts[0])
    if result.code != "00000":
        result.text = None
        return result
    else:
        poly = result.poly


    # Row Text Objects
    rowTexts = Text.objects.filter(page = page)

    lowerBound = poly['y1'] - poly['ydif'] * (percent/100) - pixels
    rowTexts = rowTexts.filter(BoundingPolys__y__gte = lowerBound)

    upperBound = poly['y2'] + poly['ydif'] * (percent/100) + pixels
    rowTexts = rowTexts.filter(BoundingPolys__y__lte = upperBound) 

    xLowerBound = poly['x1'] - poly['xdif'] * (xLowerPercent/100) - xLowerPixels
    xUpperBound = poly['x2'] + poly['xdif'] * (xUpperPercent/100) + xUpperPixels
    rowTexts = rowTexts.exclude(Q(BoundingPolys__x__gte = xLowerBound) & Q(BoundingPolys__x__lte = xUpperBound))
    
    rowTexts = rowTexts.filter() 
    
    
    if ignoreList:
        for ignore in ignoreList:
            rowTexts = rowTexts.exclude(text=ignore)
    
    # Distinct
    rowTexts = rowTexts.distinct()  

    searchStrs = action.string.split(" ")

    items = []

    for searchStr in searchStrs:
        foundTexts = []
        for t in rowTexts:
            checkStr = strCorrections(searchStr, action.remove_chars, True)
            foundStr = strCorrections(t.text, action.remove_chars, True)
            if checkStr == foundStr:
                foundTexts.append(t)
        
        
        texts = []
        xs = []
        # No results
        if len(foundTexts) == 0:
            result = Action(foundTexts,"",False,action)
            return result
        # One result
        if len(foundTexts) == 1:
            text = foundTexts[0]
            texts.append(text)
            result = processPoly(text)
            if result.code == "00000":
                testPoly = result.poly
                xs.append(testPoly['xave'])
                item = {
                    "texts" : texts,
                    "count" : 1,
                    "xs" : xs
                }
                items.append(item)
        # Multiple results
        if len(foundTexts) > 1:
            for text in foundTexts:
                texts.append(text)
                result = processPoly(text)
                if result.code == "00000":
                    testPoly = result.poly
                    xs.append(testPoly['xave'])
            item = {
                "texts" : texts,
                "count" : len(foundTexts),
                "xs" : xs
            }
            items.append(item)
    
    texts = []
    foundStr = ""

    for i, item in enumerate(items):
        # Choose best candidate of Multiple Texts
        if item['count'] > 1:
            fText = None
            minXDif = 9999999999
            for j, text in enumerate(item['texts']):
                x = item['xs'][j]
                xdif = 0
                count = 0
                for object in items:
                    if object is not item:
                        for xave in object['xs']:
                            count += 1
                            xdif += abs(xave-x)
                if count != 0:
                    xdif = xdif / count
                else:
                    xdif = 9999999999

                if xdif < minXDif:
                    minXDif = xdif
                    fText = text

        # Single Text
        else:
            fText = item['texts'][0]
        
        # Add the text to our text list
        if fText is not None:
            texts.append(fText)
            foundStr += fText.text
        else:
            result = Action(texts,foundStr,False,action)

    # Determine Column Widths
    xmin = 9999999999
    xmax = 0
    ymin = 9999999999
    ymax = 0
    for text in texts:
        result = processPoly(text)
        if result.code == "00000":
            poly = result.poly
            if poly['x1'] < xmin:
                xmin = poly['x1']
            if poly['x2'] > xmax:
                xmax = poly['x2']
            if poly['y1'] < ymin:
                ymin = poly['y1']
            if poly['y2'] > ymax:
                ymax = poly['y2']

    xdif = xmax - xmin
    
    if action.lower_offset_percent:
        lowerPercent = action.lower_offset_percent
    else:
        lowerPercent = 0
    if action.lower_offset_pixels:
        lowerPixels = action.lower_offset_pixels
    else:
        lowerPixels = 0

    if action.upper_offset_percent:
        upperPercent = action.upper_offset_percent
    else:
        upperPercent = 0
    if action.upper_offset_pixels:
        upperPixels = action.upper_offset_pixels
    else:
        upperPixels = 0

    if xdif < 1:
        result = Action(texts,foundStr,False,action)
    else:
        xmin = xmin - xdif * (lowerPercent/100) - lowerPixels
        xmax = xmax + xdif * (upperPercent/100) + upperPixels

    result = Action(texts,foundStr,True,action)
    result.column = action.startUpper
    result.colMin = xmin
    result.colMax = xmax
    result.yMin = ymin
    result.yMax = ymax
    return result

def TableRows(action, columns, page):
    rows = []

    column = None
    for col in columns:
        if col.no == action.start:
            column = col

    
    #log.debug(f"column min {column.ymin}, column max {column.ymax}")

    if column is None:
        result = None
        return result

    # Offsets
    if action.offset_percent:
        percent = action.offset_percent
    else:
        percent = 0
    
    if action.offset_pixels:
        pixel = action.offset_pixels
    else:
        pixel = 0

    # Boundaryies
    xmin = column.xmin
    xmax = column.xmax
    ymin = column.ymax
    ymax = column.ymax + (column.ymax - column.ymin)*percent/100 + pixel

    row = TableRow(action, xmin, xmax, ymin, ymax, page)
    
    for i in range(action.startLower):
        if row is not None:
            rows.append(row)
            ymin = row.ymax
            ymax = row.ymax + (row.ymax - row.ymin)*percent/100 + pixel
            row = TableRow(action, xmin, xmax, ymin, ymax, page)

    return rows

def TableRow(action, xmin,xmax,ymin,ymax, page):
    log.debug(f"ymin: {ymin}, ymax: {ymax}")
    # Texts
    texts = Text.objects.filter(page=page)
    texts = texts.filter(BoundingPolys__x__gte = xmin)
    texts = texts.filter(BoundingPolys__x__lte = xmax)
    texts = texts.filter(BoundingPolys__y__gte = ymin)
    texts = texts.filter(BoundingPolys__y__lte = ymax)

    # Distinct
    texts = texts.distinct() 

    if action.lower_offset_percent:
        lPercent = action.lower_offset_percent
    else:
        lPercent = 0
    
    if action.lower_offset_pixels:
        lPixel = action.lower_offset_pixels
    else:
        lPixel = 0

    if action.upper_offset_percent:
        uPercent = action.upper_offset_percent
    else:
        uPercent = 0
    
    if action.upper_offset_pixels:
        uPixel = action.upper_offset_pixels
    else:
        uPixel = 0

    y = 9999999999
    fText = None
    for t in texts:
        result = processPoly(t)
        if result.code == "00000":
            poly = result.poly
            if poly['yave'] < y and poly['yave'] > ymin and poly['yave'] < ymax:
                y = poly['yave']
                fText = t

    if fText is not None:
        result = processPoly(fText)
        if result.code == "00000":
            poly = result.poly
            lowerBound = poly['y1'] - poly['ydif']*lPercent/100-lPixel
            upperBound = poly['y2'] + poly['ydif']*uPercent/100+uPixel
            row = Row(lowerBound, upperBound)
            return row
        
    return None

def TableCell(action, xmin,xmax,ymin,ymax,page):
    if action.remove_chars:
        ignoreList = action.remove_chars.split('#')
    else:
        ignoreList = None

    # Texts
    texts = Text.objects.filter(page=page)
    texts = texts.filter(BoundingPolys__x__gte = xmin)
    texts = texts.filter(BoundingPolys__x__lte = xmax)
    texts = texts.filter(BoundingPolys__y__gte = ymin)
    texts = texts.filter(BoundingPolys__y__lte = ymax)
    #texts = texts.order_by('BoundingPolys__x')

    # Ignore List
    if ignoreList:
        for ignore in ignoreList:
            texts = texts.exclude(text=ignore)
    
    # Distinct
    texts = texts.distinct()

    foundStr = ""
    aTexts = []
    #print("TABLE CELL TEXTS")
    for t in texts:
        #print(f"text: {t.text}")
        result = processPoly(t)
        if result.code == "00000":
            poly = result.poly
            #print(f"xmin: {xmin}, xmax: {xmax}, ymin: {ymin}, ymax: {ymax},")
            #print(f"xave: {poly['xave']}, yave: {poly['yave']}")
            if poly['xave'] > xmin and poly['xave'] < xmax and poly['yave'] > ymin and poly['yave'] < ymax:

                mtext = strCorrections(t.text, action.remove_chars, False)
                if action.type == action.TABLECELLVALUE:
                    foundStr += mtext
                else:
                    foundStr += " " + mtext
                #print(f"foundStr: {foundStr}")
                aTexts.append(t)

    if foundStr != "":
        #log.debug("Get Value found string: %s", foundStr)

        # VALUE Only
        if action.type == action.TABLECELLVALUE:
            x = re.findall(r"\d+", foundStr)
            if len(x) == 1:
                foundStr = x[0]
            elif len(x) >= 2:
                start = re.search(x[0], foundStr)
                end = re.search(x[1], foundStr)
                if end.start() - start.end() == 1:
                    decimalPointStr = foundStr[start.end():end.start()]
                    if decimalPointStr == ".":
                        foundStr = x[0] + "." + x[1]
                    else:
                        foundStr=x[0]
                else:
                    foundStr=x[0]
            else:
                result = Action(aTexts,foundStr,False,action)
                return result
            
        # TEXTVALUE Only
        if action.type == action.TABLECELLTEXT:
            if foundStr[0] == " ":
                foundStr = foundStr[1:]
        result = Action(aTexts,foundStr,True,action)
        return result

    result = Action(None,None,False,action)
    return result


def ExtractDataBackup(document,method):
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
    # Returns a poly object from a text object

    polys = text.BoundingPolys.all()
    if polys.count() != 4:
        result = GenerateResult(resultList,15)
        result.consolLog = f"{result.consolLog} Poly Count: {polys.count()}"
        log.warning("Error%s: %s", result.code, result.consolLog)
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

def combinePolys(poly1, poly2):
    # Combines 2 polys into one big poly.

    x1 = min(poly1['x1'],poly2['x1'])
    x2 = max(poly1['x2'],poly2['x2'])
    y1 = min(poly1['y1'],poly2['y1'])
    y2 = max(poly1['y2'],poly2['y2'])

    poly = {
        'BL' : None,
        'BR' : None,
        'TL' : None,
        'TR' : None,
        'x1' : x1,
        'x2' : x2,
        'y1' : y1,
        'y2' : y2,
        'xdif' : x2 - x1,
        'ydif' : y2 - y1,
        'xave' : (x1+x2)/2,
        'yave' : (y1+y2)/2,
        'xmax' : max(x1,x2),
        'ymax' : max(y1,y2),
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

class Action:
    def __init__(self, texts, text, success, action):
        self.texts = texts
        self.text = text
        self.value = None
        self.success = success
        self.action = action
        self.tableHeader = False
        self.column = None
        self.colMin = None
        self.colMax = None
        self.yMin = None
        self.yMax = None

    def __str__(self):
        if self.success:
            return f"Action: Success, {self.action.get_type_display()}: {self.text}"
        else:
            return f"Action: Fail, {self.action.get_type_display()}: {self.action.string}"
        
class Column:
    def __init__(self, no, xmin, xmax, ymin, ymax):
        self.no = no
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

class Row:
    def __init__ (self, ymin, ymax):
        self.ymin = ymin
        self.ymax = ymax
        self.values = []
        self.texts = []
        self.units = []