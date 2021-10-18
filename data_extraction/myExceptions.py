class Error:
    def __init__(self,code,desc,log):
        self.code = code
        self.description = desc
        self.consolLog = log


errorbase = "10"
searchList = [
    Error(errorbase + "000","Error processing results from API","Error processing results from API"),
    Error(errorbase + "001","API request failed (QLD site). The website (https://geoscience.data.qld.gov.au) may be having issues.", "API request failed"),
    Error(errorbase + "002","API request failed (SA site).", "API request failed"),
    Error(errorbase + "003","No Gov_id","No Gov_id"),
    Error(errorbase + "004","",""),
    Error(errorbase + "005","Not a well report","Not a well report"),
    Error(errorbase + "006","Not a well report: multiple permits","Not a well report: multiple permits"),
    Error(errorbase + "007","?","?"),
    Error(errorbase + "008","",""),
    Error(errorbase + "009","",""),
    Error(errorbase + "010","Database error - Failed to commit new company to database.","Database error - Failed to commit new company to database."),
    Error(errorbase + "011","Database error - Failed to commit new well to database","Database error - Failed to commit new well to database."),
    Error(errorbase + "012","Well already exists in database","Failed to add well to database: Well already exists in database"),
    Error(errorbase + "013","Database error - Failed to commit new document type to database.","Database error - Failed to commit new document type to database."),
    Error(errorbase + "014","Database error - Failed to commit new document to database.","Database error - Failed to commit document to database."),
    Error(errorbase + "015","Document with same name already exists for well.","Document with same name already exists for well."),
    Error(errorbase + "016","Database error - Failed to commit new Well Class to database","Database error - Failed to commit new Well Class to database"),
    Error(errorbase + "017","Database error - Failed to commit new Well Purpose to database","Database error - Failed to commit new Well Purpose to database"),
    Error(errorbase + "018","Database error - Failed to commit new Well Status to database","Database error - Failed to commit new Well Status to database"),
    Error(errorbase + "019","Database error - Failed to commit new Report Type to database","Database error - Failed to commit new Report Type to database"),
    Error(errorbase + "020","Database error - Failed to update well to database","Database error - Failed to update well to database"),
    Error(errorbase + "021","Database error - Failed to commit new Permit to database","Database error - Failed to commit new Permit to database"),
    Error(errorbase + "022","",""),
    Error(errorbase + "023","",""),
    Error(errorbase + "024","",""),
    Error(errorbase + "025","",""),
    Error(errorbase + "026","",""),
    Error(errorbase + "027","",""),
    Error(errorbase + "028","",""),
    Error(errorbase + "029","",""),
    Error(errorbase + "030","",""), 
]

errorbase = "50"
downloadList = [
    Error(errorbase + "000", "Success", "Success"),
    Error(errorbase + "001", "Failed to create folder", "Failed to create folder"),
    Error(errorbase + "002", "Connection Failed.", "Connection Failed."),
    Error(errorbase + "003", "Failed to create file object", "Failed to create file object"),
    Error(errorbase + "004", "Failed to download file", "Failed to download file"),
    Error(errorbase + "005", "File already exists in database", "File already exists in database"),
]

errorbase = "55"
convertList = [
    Error(errorbase + "000", "Success", "Success"),
    Error(errorbase + "001", "Can't convert, Not JPEG or TIFF file", "Can't convert, Not JPEG or TIFF file"),
    Error(errorbase + "002", "Already converted", "Already converted"),
    Error(errorbase + "003", "Unable to create directory: ", "Unable to create directory."),
    Error(errorbase + "004", "Unable to save pages.", "Unable to save pages."),
    Error(errorbase + "005", "Unable to create page object in database.", "Unable to create page object in database."),
    Error(errorbase + "006", "Unable to create file object in database.", "Unable to create file object in database."),
    Error(errorbase + "007", "", ""),
    Error(errorbase + "008", "", ""),
    Error(errorbase + "009", "", ""),
    Error(errorbase + "010", "TIFF error: ", "TIFF error: "),
    Error(errorbase + "011", "JPEG error: ", "JPEG error: "),
    Error(errorbase + "012", "", ""),
    Error(errorbase + "013", "TIFF - reached 1000 pages in file: ", "TIFF - reached 1000 pages in file"),
    Error(errorbase + "014", "PDF - file too large: ", "PDF - file too large"),
]