import os
from termcolor import colored #pip install termcolor
from PIL import Image #pip install Pillow
from pdf2image import convert_from_path #pip install pdf2image and install poppler and add to PATH (https://pypi.org/project/pdf2image/)
import tempfile

Image.warnings.simplefilter('error', Image.DecompressionBombWarning)

os.system('color')

print(colored("\r\n    START\r\n",'green'))

#yourpath = os.getcwd() + "\\..\\WCR"
yourpath = "D:\\WCR"
for root, dirs, files in os.walk(yourpath, topdown=False):
    for name in files:
        #PARSE TIF FILES*************************************************************************************************************************
        if os.path.splitext(os.path.join(root, name))[1].lower() == ".tiff" or os.path.splitext(os.path.join(root, name))[1].lower() == ".tif":
            if os.path.isfile(os.path.splitext(os.path.join(root, name))[0] + "\\page1.jpg"):
                pass
            else:
                print("opening file: " + os.path.join(root, name))
                try:
                    #open tif
                    im = Image.open(os.path.join(root, name))

                    #create director
                    myPath = os.path.splitext(os.path.join(root, name))[0]
                    if(not os.path.isdir(myPath)):
                        try:
                            os.mkdir(myPath)
                        except Exception as e:
                            print(colored('Unable to create directory: ' + myPath, 'red'))

                    #loop through pages
                    for i in range(1000):
                        if(i == 999):
                            print(colored("Warning: reached 1000 pages in file %s" % name,'yellow'));
                        try:
                            #load page
                            im.seek(i)
                            outfile = os.path.splitext(os.path.join(root, name))[0] + "\\page" + str(i+1) + ".jpg"
                            try:
                                im.thumbnail(im.size)
                                im.save(outfile, "JPEG", quality=100)
                            except:
                                print(colored("failed to create JPEG: " + os.path.join(root, name) + " - Page" + str(i+1),'red'))
                        except EOFError:
                            # Not enough frames in img
                            break
                except:
                    print(colored("Failed to open: " + os.path.join(root, name) + ". Image is probably too large.",'yellow'))

        #PARSE PDF FILES********************************************************************************************
        elif os.path.splitext(os.path.join(root, name))[1].lower() == ".pdf":
            if os.path.isfile(os.path.splitext(os.path.join(root, name))[0] + "\\page1.jpg"):
                pass
            else:
                with tempfile.TemporaryDirectory() as path:
                    #create pages
                    myTry = False;
                    try:
                        pages = convert_from_path(os.path.join(root, name), output_folder=path)
                        myTry = True
                    except:
                        print(colored("File too large",'red'))
                        myTry = False

                    if(myTry):
                        #create director
                        myPath = os.path.splitext(os.path.join(root, name))[0]
                        if(not os.path.isdir(myPath)):
                            try:
                                os.mkdir(myPath)
                            except Exception as e:
                                print(colored('Unable to create directory: ' + myPath, 'red'))

                        #save pages
                        i = 1
                        for page in pages:
                            filename = os.path.splitext(os.path.join(root, name))[0] + "\\page" + str(i) + ".jpg"
                            page.save(filename, 'JPEG')
                            i = i + 1
        elif os.path.splitext(os.path.join(root, name))[1].lower() == ".jpg":
            pass
        else:
            print(colored("Skipping File with extension " + os.path.splitext(os.path.join(root, name))[1] + ": " + name))

print(colored("\r\n    FINISH",'green'))
