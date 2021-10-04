import os
from PIL import Image #pip install Pillow
from pdf2image import convert_from_path #pip install pdf2image and install poppler and add to PATH (https://pypi.org/project/pdf2image/)
import tempfile

from data_extraction.settings.base import MEDIA_ROOT
from data_extraction.myExceptions import Error, convertList as errorList

def convertFile(path):
    path = MEDIA_ROOT + path
    folder, ext = os.path.splitext(path)
    ext = ext.lower()
    name = os.path.basename(path)
    print(folder)
    print(name)
    print(ext)


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
            return convertTIFF(path,folder,name,ext)
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
            return convertPDF(path,folder,name,ext)
    else:
        #Not a Tiff or pdf
        # Handle Error
        myResult = errorList[1]
        result = Error(myResult.code,myResult.description,myResult.consolLog)
        result.description = result.description + ": " + path
        result.consolLog = result.consolLog + ": " + path
        #print(f"Error {result.code}: {result.consolLog}")
        return result


def convertTIFF(path,folder,name,ext):
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
                outfile = folder + "\\page" + str(i+1) + ".jpg"
                try:
                    im.thumbnail(im.size)
                    im.save(outfile, "JPEG", quality=100)
                except Exception as e:
                    # Handle Error
                    myResult = errorList[10]
                    result = Error(myResult.code,myResult.description,myResult.consolLog)
                    result.description = result.description + str(e)
                    print(f"Error {result.code}: {result.consolLog}")
                    print(e)
                    return result
            except EOFError:
                # Not enough frames in img
                # Handle Error
                myResult = errorList[12]
                result = Error(myResult.code,myResult.description,myResult.consolLog)
                result.description = result.description + str(EOFError)
                print(f"Error {result.code}: {result.consolLog}")
                print(EOFError)
                return result

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

def convertPDF(path,folder,name,ext):
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
        print("here")
        for i, page in enumerate(pages):
            filename = folder + '/' + "page" + str(i) + ".jpg"
            page.save(filename, 'JPEG')

    # Return Success
    myResult = errorList[0]
    result = Error(myResult.code,myResult.description,myResult.consolLog)
    return result