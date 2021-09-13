from datetime import datetime, date

#import pytz
from pytz import timezone

pathToWCRs = '/mnt/alpha/WCR'

api = 'https://geoscience.data.qld.gov.au/api/action/'
maxRows = '99999'

# For building links to WCRs
urlBase = 'https://geoscience.data.qld.gov.au'

#Owner corrections
ownerCorrections = [
    ("Amalgamated Petroleum Nl", "Amalgamated Petroleum"),
    ("Australia Pacific Lng Pty Limited","APLNG"),
    ("Australia Pacific Lng (Ironbark) Pty Limited", "APLNG (Ironbark)"),
    ("Australian Aquitaine Petroleum Pty Limited", "Australian Aquitaine Petroleum"),
    ("Beach Energy (Operations) Limited","Beach Energy"),
    ("Civil & Mining Resources Pty Ltd", "Civil & Mining Resources"),
    ("Cluff Oil (Australia) Nl", "Cluff Oil"),
    ("Icon Oil Drilling Company Pty Ltd", "Icon Oil"),
    ("Icon Oil Nl", "Icon Oil"),
    ("Meridian Oil N.L.","Meridian Oil"),
    ("Meridian Oil N. L.","Meridian Oil"),
    ("Mt Isa Mines Ltd", "Mt Isa Mines"),
    ("Oil Company Of Australia Nl", "Oil Company Of Australia"),
    ("Origin", "Origin Energy"),
    ("Origin Energy Csg Ltd", "Origin Energy"),
    ("Origin Energy Upstream Operator Pty Ltd", "Origin Energy"),
    ("Santos Ltd", "Santos"),
    ("Santos Limited", "Santos"),  
    ("Qgc", "QGC"),
    ("Qgc Pty Limited","QGC"),
    ("Queensland Gas Company Limited", "QGC"),
    ("Westside Corporation Ltd", "Westside Corporation"),
    ("Westside Corporation Pty Limited", "Westside Corporation"),
    
    ("original", "changed_to"),
]


au_tz = timezone('Australia/Brisbane')
def ConvertQLDDateTime(str):
    if(str is None or str == ""):
        return None
    else:
        #pos = str.find("T")
        dateStr = str#[0:pos]
        dateTime = datetime(int(dateStr[0:4]), int(dateStr[5:7]), int(dateStr[8:10]), int(dateStr[11:13]), int(dateStr[14:16]), int(dateStr[17:19]),int(dateStr[20:]),tzinfo=au_tz)

        return dateTime

def ConvertQLDDate(dateStr):
    if(dateStr is None or dateStr == ""):
        return None
    else: 
        myDate = date(int(dateStr[0:4]), int(dateStr[5:7]), int(dateStr[8:10]))

        return myDate