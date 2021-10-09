import os
from PIL import Image #pip install Pillow
from pdf2image import convert_from_path #pip install pdf2image and install poppler and add to PATH (https://pypi.org/project/pdf2image/)
import tempfile

from data_extraction.settings.base import MEDIA_ROOT
from data_extraction.myExceptions import Error, convertList as errorList

from data_extraction.models import Company, Data, Document, File, Page, Report, State, WellStatus, Well

def convertFile(document):
    path = document.file.file_location + document.file.file_name + document.file.file_ext
    print(path)

    path = MEDIA_ROOT + path
    folder, ext = os.path.splitext(path)
    ext = ext.lower()
    name = os.path.basename(path)


    if ext == ".tiff" or ext == ".tif":
        if os.path.isfile(folder + "\\page1.jpg"):
            #Already Converted
            # Handle Error
            myResult = errorList[2]
            result = Error(myResult.code,myResult.description,myResult.consolLog)
            result.description = result.description + ": " + path
            result.consolLog = result.consolLog + ": " + path
            #print(f"Error {result.code}: {result.consolLog}")
            return result
        else:
            return convertTIFF(path,folder,document)
    elif ext == ".pdf":
        if os.path.isfile(folder + "\\page1.jpg"):
            #Already Converted
            # Handle Error
            myResult = errorList[2]
            result = Error(myResult.code,myResult.description,myResult.consolLog)
            result.description = result.description + ": " + path
            result.consolLog = result.consolLog + ": " + path
            #print(f"Error {result.code}: {result.consolLog}")
            return result
        else:
            return convertPDF(path,folder,document)
    else:
        #Not a Tiff or pdf
        # Handle Error
        myResult = errorList[1]
        result = Error(myResult.code,myResult.description,myResult.consolLog)
        result.description = result.description + ": " + path
        result.consolLog = result.consolLog + ": " + path
        #print(f"Error {result.code}: {result.consolLog}")
        return result


def convertTIFF(path,folder,document):
    try:
        #open tif
        im = Image.open(path)

        #create director
        if(not os.path.isdir(folder)):
            try:
                os.mkdir(folder)
            except Exception as e:
                # Handle Error
                myResult = errorList[3]
                result = Error(myResult.code,myResult.description,myResult.consolLog)
                result.description = result.description + str(e)
                print(f"Error {result.code}: {result.consolLog}")
                print(e)
                return result

        #loop through pages
        for i in range(1000):
            if(i == 999):
                # Handle Error
                myResult = errorList[13]
                result = Error(myResult.code,myResult.description,myResult.consolLog)
                result.description = result.description + path
                #print(f"Error {result.code}: {result.consolLog}")
                return result
            try:
                #load page
                im.seek(i)
                filename = folder + '/' + "page" + str(i+1) + ".jpg"
                try:
                    im.thumbnail(im.size)
                    im.save(filename, "JPEG", quality=100)

                    fileSize = os.path.getsize(filename)
                    try:
                        fileObject = File.objects.create(
                            file_name = "page" + str(i+1),
                            file_ext = ".jpg",
                            file_location = document.file.file_location + document.file.file_name + '/',
                            file_size = fileSize
                        )
                        fileObject.save()

                    except Exception as e:
                        # Handle Error
                        myResult = errorList[5]
                        result = Error(myResult.code,myResult.description,myResult.consolLog)
                        result.description = result.description + str(e)
                        print(f"Error {result.code}: {result.consolLog}")
                        print(e)
                        return result
                    try:
                        page = Page.objects.create(
                            document=document, 
                            page_no = i,
                            file = fileObject,
                        )
                        page.save()
                    except Exception as e:
                        # Handle Error
                        myResult = errorList[4]
                        result = Error(myResult.code,myResult.description,myResult.consolLog)
                        result.description = result.description + str(e)
                        print(f"Error {result.code}: {result.consolLog}")
                        print(e)
                        return result

                except Exception as e:
                    # Handle Error
                    myResult = errorList[10]
                    result = Error(myResult.code,myResult.description,myResult.consolLog)
                    #result.description = result.description + str(e)
                    print(f"Error {result.code}: {result.consolLog}")
                    print(e)
                    return result
            except:
                # End of file
                break

    except Exception as e:
        # Handle Error
        myResult = errorList[10]
        result = Error(myResult.code,myResult.description,myResult.consolLog)
        result.description = result.description + str(e)
        print(f"Error {result.code}: {result.consolLog}")
        print(e)
        return result

    # Return Success
    myResult = errorList[0]
    result = Error(myResult.code,myResult.description,myResult.consolLog)
    return result

def convertPDF(path,folder,document):
    try:
        with tempfile.TemporaryDirectory() as tempPath:
            #create pages
            try:
                pages = convert_from_path(path, output_folder=tempPath)
            except Exception as e:
                # Handle Error
                myResult = errorList[14]
                result = Error(myResult.code,myResult.description,myResult.consolLog)
                result.description = result.description + str(e)
                print(f"Error {result.code}: {result.consolLog}")
                print(e)
                return result

            #create director
            if(not os.path.isdir(folder)):
                try:
                    os.mkdir(folder)
                except Exception as e:
                    # Handle Error
                    myResult = errorList[3]
                    result = Error(myResult.code,myResult.description,myResult.consolLog)
                    result.description = result.description + str(e)
                    print(f"Error {result.code}: {result.consolLog}")
                    print(e)
                    return result

            #save pages
            try:
                for i, file in enumerate(pages):
                    filename = folder + '/' + "page" + str(i) + ".jpg"
                    file.save(filename, 'JPEG')
                    fileSize = os.path.getsize(filename)

                    try:
                        fileObject = File.objects.create(
                            file_name = "page" + str(i),
                            file_ext = ".jpg",
                            file_location = document.file.file_location + document.file.file_name + '/',
                            file_size = fileSize
                        )
                        fileObject.save()

                    except Exception as e:
                        # Handle Error
                        myResult = errorList[5]
                        result = Error(myResult.code,myResult.description,myResult.consolLog)
                        result.description = result.description + str(e)
                        print(f"Error {result.code}: {result.consolLog}")
                        print(e)
                        return result
                    try:
                        page = Page.objects.create(
                            document=document, 
                            page_no = i,
                            file = fileObject,
                        )
                        page.save()
                    except Exception as e:
                        # Handle Error
                        myResult = errorList[4]
                        result = Error(myResult.code,myResult.description,myResult.consolLog)
                        result.description = result.description + str(e)
                        print(f"Error {result.code}: {result.consolLog}")
                        print(e)
                        return result


            except Exception as e:
                # Handle Error
                myResult = errorList[4]
                result = Error(myResult.code,myResult.description,myResult.consolLog)
                result.description = result.description + str(e)
                print(f"Error {result.code}: {result.consolLog}")
                print(e)
                return result
    except:
        # Handle Error
        myResult = errorList[11]
        result = Error(myResult.code,myResult.description,myResult.consolLog)
        result.description = result.description + str(e)
        print(f"Error {result.code}: {result.consolLog}")
        print(e)
        return result

    # Return Success
    myResult = errorList[0]
    result = Error(myResult.code,myResult.description,myResult.consolLog)
    return result