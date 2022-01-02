class Result:
    def __init__(self,code,desc,log):
        self.code = code
        self.description = desc
        self.consolLog = log

def GenerateResult(list,id):
    myResult = list[id]
    return Result(myResult.code,myResult.description,myResult.consolLog)

def PrintResultLog(result):
    print(f"Error {result.code}: {result.consolLog}")

codeBase = "10"
searchList = [
    Result("00000","Success","Success"),
    Result(codeBase + "001","API request failed (QLD site). The website (https://geoscience.data.qld.gov.au) may be having issues.", "API request failed"),
    Result(codeBase + "002","API request failed (SA site).", "API request failed"),
    Result(codeBase + "003","No Gov_id","No Gov_id"),
    Result(codeBase + "004","Error processing results from API","Error processing results from API"),
    Result(codeBase + "005","Not a well report","Not a well report"),
    Result(codeBase + "006","Not a well report: multiple permits","Not a well report: multiple permits"),
    Result(codeBase + "007","?","?"),
    Result(codeBase + "008","API error","Result field data error"),
    Result(codeBase + "009","",""),
    Result(codeBase + "010","Database error - Failed to commit new company to database.","Database error - Failed to commit new company to database."),
    Result(codeBase + "011","Database error - Failed to commit new well to database","Database error - Failed to commit new well to database."),
    Result(codeBase + "012","Well already exists in database","Failed to add well to database: Well already exists in database"),
    Result(codeBase + "013","Database error - Failed to commit new document type to database.","Database error - Failed to commit new document type to database."),
    Result(codeBase + "014","Database error - Failed to commit new document to database.","Database error - Failed to commit document to database."),
    Result(codeBase + "015","Document with same name already exists for well.","Document with same name already exists for well."),
    Result(codeBase + "016","Database error - Failed to commit new Well Class to database","Database error - Failed to commit new Well Class to database"),
    Result(codeBase + "017","Database error - Failed to commit new Well Purpose to database","Database error - Failed to commit new Well Purpose to database"),
    Result(codeBase + "018","Database error - Failed to commit new Well Status to database","Database error - Failed to commit new Well Status to database"),
    Result(codeBase + "019","Database error - Failed to commit new Report Type to database","Database error - Failed to commit new Report Type to database"),
    Result(codeBase + "020","Database error - Failed to update well to database","Database error - Failed to update well to database"),
    Result(codeBase + "021","Database error - Failed to commit new Permit to database","Database error - Failed to commit new Permit to database"),
    Result(codeBase + "022","Database error - Failed to update report to database","Database error - Failed to update report to database"),
    Result(codeBase + "023","",""),
]

codeBase = "50"
downloadList = [
    Result("00000", "Success", "Success"),
    Result(codeBase + "001", "Failed to create folder", "Failed to create folder"),
    Result(codeBase + "002", "Connection Failed.", "Connection Failed."),
    Result(codeBase + "003", "Failed to create file object", "Failed to create file object"),
    Result(codeBase + "004", "Failed to download file", "Failed to download file"),
    Result(codeBase + "005", "File already exists in database", "File already exists in database"),
    Result(codeBase + "006", "Failed to delete file", "Failed to delete file"),
    Result(codeBase + "007", "Failed to delete directory", "Failed to delete directory"),
    Result(codeBase + "008", "Failed to zip file", "Failed to zip file"),
    Result(codeBase + "009", "Failed to upload to AWS Server", "Failed to upload to S3"),
    Result(codeBase + "010", "File does not exist.", "S3 file does not exist."),
    Result(codeBase + "011", "S3 File Error", "S3 File Error"),
    Result(codeBase + "012", "File does not exist.", "Local file does not exist."),
    Result(codeBase + "013", "Local file error.", "Local file error."),
    Result(codeBase + "014", "", ""),
    Result(codeBase + "015", "", ""),
]

codeBase = "55"
convertList = [
    Result("00000", "Success", "Success"),
    Result(codeBase + "001", "Can't convert, Not JPEG or TIFF file", "Can't convert, Not JPEG or TIFF file"),
    Result(codeBase + "002", "Already converted", "Already converted"),
    Result(codeBase + "003", "Unable to create directory: ", "Unable to create directory."),
    Result(codeBase + "004", "Unable to save pages.", "Unable to save pages."),
    Result(codeBase + "005", "Unable to create page object in database.", "Unable to create page object in database."),
    Result(codeBase + "006", "Unable to create file object in database.", "Unable to create file object in database."),
    Result(codeBase + "007", "Error saving PDF page.", "Error saving PDF page."),
    Result(codeBase + "008", "", ""),
    Result(codeBase + "009", "", ""),
    Result(codeBase + "010", "TIFF error: ", "TIFF error: "),
    Result(codeBase + "011", "JPEG error: ", "JPEG error: "),
    Result(codeBase + "012", "", ""),
    Result(codeBase + "013", "TIFF - reached 1000 pages in file: ", "TIFF - reached 1000 pages in file"),
    Result(codeBase + "014", "PDF - file too large: ", "PDF - file too large"),
]