import io

from data_extraction.models import BoundingPoly, Company, Data, Document, File, Page, Permit, Report, ReportType, State, Text, Well, WellClass, WellStatus, WellPurpose
from django.conf import settings

# Imports the Google Cloud client library
from google.cloud import vision
from google.protobuf.json_format import MessageToJson


def getDocumentText(document):
    pages = Page.objects.filter(document = document, extracted = False).all()

    for page in pages:
        file = page.file
        path = settings.MEDIA_ROOT + file.file_location + file.file_name + file.file_ext

        pageTexts = getTextArray(path)


        i = 0
        for pageText in pageTexts:
            i = i + 1
            if(len(pageText.description) > 255):
                print(str(i) + ": " + pageText.description)
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

    return ("success")

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

    