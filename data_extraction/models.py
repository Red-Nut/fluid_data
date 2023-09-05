# Django imports.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy  as _
from django.conf import settings

class CreatedModifiedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ***************************** Files ***************************** 

class File(CreatedModifiedModel):
    file_name = models.CharField(max_length=255)
    file_ext = models.CharField(max_length=20)
    file_location = models.TextField()
    file_size = models.IntegerField()
    
    def __str__(self):
        return f"{self.file_name}.{self.file_ext}"

    def __repr__(self):
        str = "Id: {}, file name: {}, location: {}\n" 
        str =str.format( self.id, self.file_name + self.file_ext, self.file_location)
        return str
    
    def path(self):
        path = settings.MEDIA_ROOT + self.file_location + self.file_name + self.file_ext
        return path

# ***************************** Package ***************************** 
class Package(CreatedModifiedModel):
    gov_id = models.CharField(max_length=100, unique=True)
    modified = models.DateTimeField(null=True, blank=True)
    checked = models.DateTimeField(auto_now=True)
    success = models.BooleanField(default=False)
    errorCodes = models.CharField(max_length=100, null=True, blank=True)
    error = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"{self.gov_id}"

# ***************************** Wells ***************************** 

class Company(CreatedModifiedModel):
    company_name = models.CharField(max_length = 255, unique = True)

    def __str__(self):
        return f"{self.company_name}"

    def __repr__(self):
        str = "Id: {}, name: {}\n" 
        str =str.format( self.id, self.company_name)
        return str

class State(CreatedModifiedModel):
    name_long = models.CharField(max_length=50)
    name_short = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name_short}"

    def __repr__(self):
        str = "Id: {}, name: {}\n" 
        str =str.format( self.id, self.name_long)
        return str

class Permit(CreatedModifiedModel):
    permit_number = models.CharField(max_length=20)

    def __str__(self):
	    return f"{self.permit_number}"

class WellStatus(CreatedModifiedModel):
    status_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.status_name}"

    def __repr__(self):
        str = "Id: {}, status_name: {}\n" 
        str =str.format( self.id, self.status_name)
        return str

class WellClass(CreatedModifiedModel):
    class_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.class_name}"

    def __repr__(self):
        str = "Id: {}, class_name: {}\n" 
        str =str.format( self.id, self.class_name)
        return str

class WellPurpose(CreatedModifiedModel):
    purpose_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.purpose_name}"

    def __repr__(self):
        str = "Id: {}, purpose_name: {}\n" 
        str =str.format( self.id, self.purpose_name)
        return str

class Well(CreatedModifiedModel):
    gov_id = models.CharField(max_length=100, unique=True)
    well_name = models.CharField(max_length=255, unique=True) 
    owner = models.ForeignKey(
        Company, 
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    state = models.ForeignKey(
        State, 
        on_delete=models.RESTRICT
    )
    permit = models.ForeignKey(
        Permit, 
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    )
    status = models.ForeignKey(
        WellStatus, 
        on_delete=models.RESTRICT
    )
    well_class = models.ForeignKey(
        WellClass, 
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    ) 
    purpose = models.ForeignKey(
        WellPurpose, 
        null=True,
        blank=True,
        on_delete=models.RESTRICT
    )  
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    rig_release = models.DateField(null=True, blank=True)
    package = models.ForeignKey(
        Package, 
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.well_name}"

    def __repr__(self):
        str = "Id: {}, name: {}\n" 
        str =str.format( self.id, self.well_name)
        return str

    @property
    def url(self):
        return f"https://geoscience.data.qld.gov.au/borehole/{self.gov_id}"


#  ***************************** Documents  ***************************** 

class ReportType(CreatedModifiedModel):
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type_name}"

class Report(CreatedModifiedModel):
    gov_id = models.CharField(max_length=100) 
    gov_report_name = models.CharField(max_length=255)
    gov_creator = models.CharField(max_length=255) 
    gov_created = models.DateTimeField(null=True, blank=True)
    gov_modified = models.DateTimeField(null=True, blank=True)
    gov_dataset_completion_date = models.DateField(null=True, blank=True)
    gov_open_file_date = models.DateField(null=True, blank=True)
    report_name = models.CharField(max_length=255)
    report_type = models.ForeignKey(
        ReportType, 
        on_delete=models.RESTRICT
    )
    well = models.ForeignKey(
        Well,
        null=True, 
        blank=True,
        on_delete=models.CASCADE,
        related_name="reports"
    )
    report_owner = models.ForeignKey(
        Company,
        null=True, 
        blank=True,
        on_delete=models.RESTRICT,
        related_name="reports"
    )

    url = models.TextField(max_length=1000,null=True, blank=True)

    def __str__(self):
	    return f"{self.report_name}"

class DataType(CreatedModifiedModel):
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type_name.capitalize()}"

class OtherData(CreatedModifiedModel):
    gov_id = models.CharField(max_length=100) 
    gov_report_name = models.CharField(max_length=255)
    gov_creator = models.CharField(max_length=255) 
    gov_created = models.DateTimeField(null=True, blank=True)
    gov_modified = models.DateTimeField(null=True, blank=True)
    gov_dataset_completion_date = models.DateField(null=True, blank=True)
    gov_open_file_date = models.DateField(null=True, blank=True)
    data_name = models.CharField(max_length=255)
    data_type = models.ForeignKey(
        DataType, 
        on_delete=models.RESTRICT
    )
    url = models.TextField(max_length=1000,null=True, blank=True)
    package = models.ForeignKey(
        Package,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="documents"
    )

class Document(CreatedModifiedModel):
    MISSING = 1
    DOWNLOADED = 2
    IGNORED = 3
    STATUS = (
        (MISSING, _('Missing')),
        (DOWNLOADED, _('Downloaded')),
        (IGNORED, _('Ignored')),
    )

    NOTCONVERTED=1
    CONVERTED=2
    CONVERSION = (
        (NOTCONVERTED, _('Not Converted')),
        (CONVERTED, _('Converted')),
        (IGNORED, _('Ignored')),
    )
    
    document_name = models.CharField(max_length=255)
    well = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        related_name="documents", 
        null=True,
        blank=True
    )
    report = models.ForeignKey(
        Report,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    file = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    url = models.TextField(max_length=1000,null=True)
    gov_id = models.CharField(max_length=100, unique=True, null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=1,
    )
    converted = models.BooleanField(default=False, null=True)
    conversion_status = models.PositiveSmallIntegerField(
        choices=CONVERSION,
        default=1,
    )

    #class Meta:
        #unique_together=('well_id', 'document_name')

    class Meta:
        ordering = ('well__id','document_name')

    def __str__(self):
        return f"{self.document_name}"

    def __repr__(self):
        str = "Id: {}, well_id: {}, name: {}, file_id: {}\n" 
        str =str.format( self.id, self.well.id, self.document_name, self.file)
        return str

    @property
    def link(self):
        if(self.file is None):
            link = None
        else:
            link = settings.MEDIA_URL + self.file.file_location + self.file.file_name + '.' + self.file.file_ext.replace(".","")

        return link
    
    @property
    def document_name_title_case(self):
        return self.document_name.title()
    
    @property
    def document_type(self):
        if self.file is not None:
            return self.file.file_ext[1:].lower()
        elif self.url is not None:
            x = len(self.url) - self.url.rfind('.') -1
            ext = self.url[-x:].lower()
            return ext
        else:
            return 'Unknown'
    
    def file_ext(self):
        if self.file is not None:
            return self.file.file_ext.lower()
        elif self.url is not None:
            x = len(self.url) - self.url.rfind('.')
            ext = self.url[-x:].lower()
            return ext
        else:
            return '.Unknown'

# ***************************** Page Text  ***************************** 

class Page(CreatedModifiedModel):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="pages"
    )
    page_no = models.PositiveIntegerField() 
    file = models.ForeignKey(
        File, 
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    extracted = models.BooleanField()

    class Meta:
        unique_together=('document_id', 'page_no')

    def __str__(self):
        return f"Page: {self.page_no} ({self.document})"

    def __repr__(self):
        str = "Id: {}, document id: {}, page no: {}, file id: {}\n" 
        str =str.format( self.id, self.document.id, self.page_no, self.file.id)
        return str
    
    @property
    def get_page(self):
        return f"Page {self.page_no}"
    
    @property
    def link(self):
        if(self.file is None):
            link = None
        else:
            link = settings.MEDIA_URL + self.file.file_location + self.file.file_name + '.' + self.file.file_ext.replace(".","")

        return link

class Text(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="texts"
    )
    text = models.CharField(max_length=255)

    def __str__(self):
	    return f"Page {self.page.page_no}: {self.text}"

class BoundingPoly(models.Model):
    text = models.ForeignKey(
        Text,
        on_delete=models.CASCADE,
        related_name="BoundingPolys"
    )
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        ordering = ('x','y')

    def __str__(self):
	    return f"({self.x},{self.y}) {self.text.text}"

 # ***************************** Data  ***************************** 
class Unit(CreatedModifiedModel):
    name = models.CharField(max_length=20)
    metric_units = models.CharField(max_length=20)
    metric_conversion = models.FloatField()
    imperial_units = models.CharField(max_length=20)
    imperial_conversion = models.FloatField()

    def __str__(self):
        return f"{self.name}"

    @property
    def get_units_with_brakets(self):
        if self.name=='text':
            return ""
        else:
            return f"({self.metric_units})"

class ExtractedDataTypes(CreatedModifiedModel):
    name = models.CharField(max_length=100)
    value1 = models.CharField(max_length=100, null=True)
    value2 = models.CharField(max_length=100, null=True)
    value3 = models.CharField(max_length=100, null=True)
    value4 = models.CharField(max_length=100, null=True)
    value5 = models.CharField(max_length=100, null=True)
    value6 = models.CharField(max_length=100, null=True)
    value7 = models.CharField(max_length=100, null=True)
    value8 = models.CharField(max_length=100, null=True)
    value9 = models.CharField(max_length=100, null=True)
    value10 = models.CharField(max_length=100, null=True)
    value11 = models.CharField(max_length=100, null=True)
    value12 = models.CharField(max_length=100, null=True)
    value13 = models.CharField(max_length=100, null=True)
    value14 = models.CharField(max_length=100, null=True)
    value15 = models.CharField(max_length=100, null=True)
    value16 = models.CharField(max_length=100, null=True)
    value17 = models.CharField(max_length=100, null=True)
    value18 = models.CharField(max_length=100, null=True)
    value19 = models.CharField(max_length=100, null=True)
    value20 = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def columns(self):
        if self.value20:
            return 20
        if self.value19:
            return 19
        if self.value18:
            return 18
        if self.value17:
            return 17
        if self.value16:
            return 16
        if self.value15:
            return 15
        if self.value14:
            return 14
        if self.value13:
            return 13
        if self.value12:
            return 12
        if self.value11:
            return 11
        if self.value10:
            return 10
        if self.value9:
            return 9
        if self.value8:
            return 8
        if self.value7:
            return 7
        if self.value6:
            return 6
        if self.value5:
            return 5
        if self.value4:
            return 4
        if self.value3:
            return 3
        if self.value2:
            return 2
        if self.value1:
            return 1
        return 0

class ExtractionMethod(CreatedModifiedModel):
    name = models.CharField(max_length=100)
    data_type = models.ForeignKey(
        ExtractedDataTypes,
        null=False,
        on_delete=models.RESTRICT,
        related_name="methods"
    ) 
    company = models.ForeignKey(
        Company,
        null=True,
        on_delete=models.RESTRICT,
        default=None
    )
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def get_company(self):
        if self.company is None:
            return "-"
        else:
            return self.company

class ExtractionAction(CreatedModifiedModel):
    INITIAL = 0
    NEXT=1
    SEARCH=2
    VALUE=3
    TEXTVALUE=4
    SAVE = 5
    NEXTDATA = 6
    REPEAT = 99
    TABLEHEADER = 11
    TABLEROW = 12
    TABLECELLVALUE = 13
    TABLECELLTEXT = 14
    TYPE = (
        (INITIAL, _('Initial Action')),
        (NEXT, _('Immediately Next Text')),
        (SEARCH, _('Find Text')),
        (VALUE, _('Get Value')),
        (TEXTVALUE, _('Get Text Value')),
        (NEXTDATA, _('Next Data Row')),
        (SAVE, _('Save Data')),
        (TABLEHEADER, _('Table Header')),
        (TABLEROW, _('Table Row')),
        (TABLECELLVALUE, _('Table Cell Value')),
        (TABLECELLTEXT, _('Table Cell Text')),
    )

    LEFT=1
    RIGHT=2
    UP=3
    DOWN=4
    DIRECTION = (
        (LEFT, _('Left')),
        (RIGHT, _('Right')),
        (UP, _('Up')),
        (DOWN, _('Down')),
    )

    START=2
    MID = 1
    END = 0
    BOUNDS = (
        (START, _('Start')),
        (MID, _('Middle')),
        (END, _('Other End')),
    )

    string = models.CharField(max_length=100, null=True)

    type = models.PositiveSmallIntegerField(
        choices=TYPE,
    )
    direction = models.PositiveSmallIntegerField(
        choices=DIRECTION,
        null=True
    ) 
    start = models.PositiveSmallIntegerField(null=True)
    offset_percent = models.SmallIntegerField(null=True) # percentage offset, 1 = 1%, can be negative. 
    offset_pixels = models.SmallIntegerField(null=True) # pixel offset, 1 = 1px, can be negative
                                                        # in table header used for y variation

    startLower = models.PositiveSmallIntegerField(null=True) 
    startUpper = models.PositiveSmallIntegerField(null=True) # Also Column Number
                                                             # Also used to specifiy step range repeating

    unit = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT
    ) 

    lower_bound = models.PositiveSmallIntegerField(
        choices=BOUNDS,
        null=True
    )
    lower_offset_percent = models.SmallIntegerField(null=True) # percentage offset, 1 = 1%, can be negative
    lower_offset_pixels = models.SmallIntegerField(null=True) # pixel offset, 1 = 1px, can be negative
                                                                # in table initial used to set the x range the the intial column occupies
                                                                # in table header used to set the x range the the column occupies

    upper_bound = models.PositiveSmallIntegerField(
        choices=BOUNDS,
        null=True
    )
    upper_offset_percent = models.SmallIntegerField(null=True) # percentage offset, 1 = 1%, can be negative
    upper_offset_pixels = models.SmallIntegerField(null=True) # pixel offset, 1 = 1px, can be negative
                                                                # in table initial used to set the x range the the intial column occupies
                                                                # in table header used to set the x range the the column occupies

    
    remove_chars = models.CharField( # char list separated by hash symbol
        max_length=100, 
        null=True, 
        default=" #(#)#|"
    )
    can_fail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_type_display()}: {self.string}"

    @property
    def string_display(self):
        if self.string is None:
            if self.type == self.VALUE or self.type == self.TEXTVALUE or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return self.string

    @property
    def direction_display(self):
        if self.direction is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return self.get_direction_display()

    @property
    def start_display(self):
        if self.start is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"Step {self.start} going {self.direction_display}"

    @property
    def lower_bound_start(self):
        if self.startLower:
            return self.startLower
        else: 
            return self.start

    @property
    def lower_bound_display(self):
        if self.lower_bound is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"{self.get_lower_bound_display()}"

    @property
    def lower_offset_percent_display(self):
        if self.lower_offset_percent is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"{self.lower_offset_percent}%"

    @property
    def lower_offset_pixels_display(self):
        if self.lower_offset_pixels is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"{self.lower_offset_pixels}px"
        
    @property
    def lower_bound_summary(self):
        if self.start is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            myStr = f"{self.get_lower_bound_display()} of Step {self.lower_bound_start}"
            
            if self.lower_offset_percent:
                myStr = f"{myStr} ({self.lower_offset_percent}%)"
            if self.lower_offset_pixels:
                myStr = f"{myStr} ({self.lower_offset_pixels}px)"

            return myStr

    @property
    def upper_bound_start(self):
        if self.startUpper:
            return self.startUpper
        else: 
            return self.start

    @property
    def upper_bound_display(self):
        if self.upper_bound is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"{self.get_upper_bound_display()}"

    @property
    def upper_offset_percent_display(self):
        if self.upper_offset_percent is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"{self.upper_offset_percent}%"

    @property
    def upper_offset_pixels_display(self):
        if self.upper_offset_pixels is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            return f"{self.upper_offset_pixels}px"
        
    @property
    def upper_bound_summary(self):
        if self.start is None:
            if self.type == self.INITIAL or self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return "Error"
        else:
            myStr = f"{self.get_upper_bound_display()} of Step {self.upper_bound_start}"
            
            if self.upper_offset_percent:
                myStr = f"{myStr} ({self.upper_offset_percent}%)"
            if self.upper_offset_pixels:
                myStr = f"{myStr} ({self.upper_offset_pixels}px)"

            return myStr

    @property
    def remove_chars_display(self):
        if self.remove_chars:
            return self.remove_chars.replace("#", " ")
        else:
            if self.type == self.SAVE or self.NEXTDATA:
                return "-"
            else:
                return self.remove_chars
    

class ExtractionActions(models.Model):
    method = models.ForeignKey(
        ExtractionMethod,
        null=False,
        on_delete=models.CASCADE,
        related_name="actions"
    ) 
    action = models.ForeignKey(
        ExtractionAction,
        null=False,
        on_delete=models.CASCADE,
        related_name="methods"
    ) 
    
    order = models.IntegerField()

    class Meta:
        ordering = ('order',)

class Data(CreatedModifiedModel):
    page = models.ForeignKey(
        Page,
        null=False,
        on_delete=models.CASCADE,
        related_name="datas"
    ) 
    extraction_method = models.ForeignKey(
        ExtractionMethod,
        null=False,
        on_delete=models.RESTRICT,
        related_name="datas"
    ) 

    value = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text = models.CharField(max_length=100, null=True)
    unit = models.ForeignKey(
        Unit,
        null=False,
        on_delete=models.RESTRICT,
        related_name="first_units"
    )

    value2 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text2 = models.CharField(max_length=100, null=True)
    unit2 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="second_units"
    ) 

    value3 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text3 = models.CharField(max_length=100, null=True)
    unit3 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="third_units"
    ) 

    value4 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text4 = models.CharField(max_length=100, null=True)
    unit4 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="forth_units"
    ) 

    value5 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text5 = models.CharField(max_length=100, null=True)
    unit5 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="fifth_units"
    ) 

    value6 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text6 = models.CharField(max_length=100, null=True)
    unit6 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="sixth_units"
    ) 

    value7 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text7 = models.CharField(max_length=100, null=True)
    unit7 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="seventh_units"
    ) 

    value8 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text8 = models.CharField(max_length=100, null=True)
    unit8 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="eigth_units"
    ) 

    value9 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text9 = models.CharField(max_length=100, null=True)
    unit9 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="ninth_units"
    ) 

    value10 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text10 = models.CharField(max_length=100, null=True)
    unit10 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="tenth_units"
    ) 

    value11 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text11 = models.CharField(max_length=100, null=True)
    unit11 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="eleventh_units"
    ) 

    value12 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text12 = models.CharField(max_length=100, null=True)
    unit12 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="twelfth_units"
    ) 

    value13 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text13 = models.CharField(max_length=100, null=True)
    unit13 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="thirteenth_units"
    ) 

    value14 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text14 = models.CharField(max_length=100, null=True)
    unit14 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="fourteenth_units"
    ) 

    value15 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text15 = models.CharField(max_length=100, null=True)
    unit15 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="fifthteenth_units"
    ) 

    value16 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text16 = models.CharField(max_length=100, null=True)
    unit16 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="sixteenth_units"
    ) 

    value17 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text17 = models.CharField(max_length=100, null=True)
    unit17 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="seventeenth_units"
    ) 

    value18 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text18 = models.CharField(max_length=100, null=True)
    unit18 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="eighteenth_units"
    ) 

    value19 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text19 = models.CharField(max_length=100, null=True)
    unit19 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="nineteenth_units"
    ) 

    value20 = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True) 
    text20 = models.CharField(max_length=100, null=True)
    unit20 = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.RESTRICT,
        related_name="twentieth_units"
    ) 

    def __str__(self):
        return f"{self.page}"

    def __repr__(self):
        str = "Id: {}, page id: {}\n" 
        str =str.format( self.id, self.page)
        return str

    def name(self):
        return self.extraction_method.data_type.name
    
    class Meta:
        unique_together=('page', 'extraction_method', 'value', 'text', 'unit', 
                         'value2', 'text2', 'unit2', 
                         'value3', 'text3', 'unit3', 
                         'value4', 'text4', 'unit4',
                         )
    
    def valueToDisplay(self, unit, value, text):
        if value or text:
            if unit:
                if unit.name == "text":
                    if text:
                        return text
                    else:
                        return '-'
                if value:
                    try:
                        value = unit.metric_conversion * float(value)
                        return f"{value}"
                    except:
                        return 'Error'
                else:
                    return '-'
            else:
                return 'Error: Unit not specified.'
        else:
            return '-'
        
    def valueWithUnits(self, unit, value, text):
        if value or text:
            if unit:
                if unit.name == "text":
                    if text:
                        return text
                    else:
                        return '-'
                if value:
                    try:
                        value = unit.metric_conversion * float(value)
                        return f"{value}{unit.metric_units}"
                    except:
                        return 'Error'
                else:
                    return '-'
            else:
                return 'Error: Unit not specified.'
        else:
            return '-'

    @property
    def get_value(self):
        return self.valueToDisplay(self.unit, self.value, self.text)
    @property
    def get_value1(self):
        return self.valueToDisplay(self.unit, self.value, self.text)
    @property
    def get_value2(self):
        return self.valueToDisplay(self.unit2, self.value2, self.text2)
    @property
    def get_value3(self):
        return self.valueToDisplay(self.unit3, self.value3, self.text3)
    @property
    def get_value4(self):
        return self.valueToDisplay(self.unit4, self.value4, self.text4)
    @property
    def get_value5(self):
        return self.valueToDisplay(self.unit5, self.value5, self.text5)
    @property
    def get_value6(self):
        return self.valueToDisplay(self.unit6, self.value6, self.text6)
    @property
    def get_value7(self):
        return self.valueToDisplay(self.unit7, self.value7, self.text7)
    @property
    def get_value8(self):
        return self.valueToDisplay(self.unit8, self.value8, self.text8)
    @property
    def get_value9(self):
        return self.valueToDisplay(self.unit9, self.value9, self.text9)
    @property
    def get_value10(self):
        return self.valueToDisplay(self.unit10, self.value10, self.text10)
    @property
    def get_value11(self):
        return self.valueToDisplay(self.unit11, self.value11, self.text11)
    @property
    def get_value12(self):
        return self.valueToDisplay(self.unit12, self.value12, self.text12)
    @property
    def get_value13(self):
        return self.valueToDisplay(self.unit13, self.value13, self.text13)
    @property
    def get_value14(self):
        return self.valueToDisplay(self.unit14, self.value14, self.text14)
    @property
    def get_value15(self):
        return self.valueToDisplay(self.unit15, self.value15, self.text15)
    @property
    def get_value16(self):
        return self.valueToDisplay(self.unit16, self.value16, self.text16)
    @property
    def get_value17(self):
        return self.valueToDisplay(self.unit17, self.value17, self.text17)
    @property
    def get_value18(self):
        return self.valueToDisplay(self.unit18, self.value18, self.text18)
    @property
    def get_value19(self):
        return self.valueToDisplay(self.unit19, self.value19, self.text19)
    @property
    def get_value20(self):
        return self.valueToDisplay(self.unit20, self.value20, self.text20)
    
    @property
    def get_value_with_units(self):
        return self.valueWithUnits(self.unit, self.value, self.text)
    @property
    def get_value1_with_units(self):
        return self.valueWithUnits(self.unit, self.value, self.text)
    @property
    def get_value2_with_units(self):
        return self.valueWithUnits(self.unit2, self.value2, self.text2)
    @property
    def get_value3_with_units(self):
        return self.valueWithUnits(self.unit3, self.value3, self.text3)
    @property
    def get_value4_with_units(self):
        return self.valueWithUnits(self.unit4, self.value4, self.text4)
    @property
    def get_value5_with_units(self):
        return self.valueWithUnits(self.unit5, self.value5, self.text5)
    @property
    def get_value6_with_units(self):
        return self.valueWithUnits(self.unit6, self.value6, self.text6)
    @property
    def get_value7_with_units(self):
        return self.valueWithUnits(self.unit7, self.value7, self.text7)
    @property
    def get_value8_with_units(self):
        return self.valueWithUnits(self.unit8, self.value8, self.text8)
    @property
    def get_value9_with_units(self):
        return self.valueWithUnits(self.unit9, self.value9, self.text9)
    @property
    def get_value10_with_units(self):
        return self.valueWithUnits(self.unit10, self.value10, self.text10)
    @property
    def get_value11_with_units(self):
        return self.valueWithUnits(self.unit11, self.value11, self.text11)
    @property
    def get_value12_with_units(self):
        return self.valueWithUnits(self.unit12, self.value12, self.text12)
    @property
    def get_value13_with_units(self):
        return self.valueWithUnits(self.unit13, self.value13, self.text13)
    @property
    def get_value14_with_units(self):
        return self.valueWithUnits(self.unit14, self.value14, self.text14)
    @property
    def get_value15_with_units(self):
        return self.valueWithUnits(self.unit15, self.value15, self.text15)
    @property
    def get_value16_with_units(self):
        return self.valueWithUnits(self.unit16, self.value16, self.text16)
    @property
    def get_value17_with_units(self):
        return self.valueWithUnits(self.unit17, self.value17, self.text17)
    @property
    def get_value18_with_units(self):
        return self.valueWithUnits(self.unit18, self.value18, self.text18)
    @property
    def get_value19_with_units(self):
        return self.valueWithUnits(self.unit19, self.value19, self.text19)
    @property
    def get_value20_with_units(self):
        return self.valueWithUnits(self.unit20, self.value20, self.text20)

# ***************************** USER Extensions  ***************************** 

class UserFileBucket(CreatedModifiedModel):
    REQUESTED = 1
    PREPARING = 2
    READY = 3
    ARCHIVED = 4
    STATUS = (
        (REQUESTED, _('Requested')),
        (PREPARING, _('Preparing files')),
        (READY, _('Ready to download')),
        (ARCHIVED, _('Archived')),
    )

    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=1,
    )
    zipSize = models.PositiveIntegerField(null=True, blank=True)

class FileBucketFiles(models.Model):
    bucket = models.ForeignKey(UserFileBucket, on_delete=models.CASCADE, related_name="documents")
    document = models.ForeignKey(Document,on_delete=models.CASCADE)


class Organisation(CreatedModifiedModel):
    organisation_name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.organisation_name}"

    def __repr__(self):
        str = "Id: {}, name: {}\n" 
        str =str.format( self.id, self.organisation_name)
        return str

class UserProfile(models.Model):
    ACTIVE = 1
    SUSPENDED = 2
    REQUESTED = 3
    DELETED = 9
    STATUS = (
        (ACTIVE, _('Active')),
        (SUSPENDED, _('Suspended')),
        (REQUESTED, _('Requested')),
        (DELETED, _('Deleted')),
    )

    ADMIN = 0
    STANDARD = 1
    PRIVILEGE = (
        (ADMIN, _('Admin')),
        (STANDARD, _('Standard')),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(
        Organisation, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles"
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=1,
    )
    privilege = models.PositiveSmallIntegerField(
        choices=PRIVILEGE,
        default=1,
    )

    metric_units = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}"

    def __repr__(self):
        str = "Id: {}, name: {}\n" 
        str =str.format( self.id, self.user.username)
        return str

# ***************************** Database Functions  ***************************** 
class CompanyNameCorrections(models.Model):
    alternateName = models.CharField(max_length=255, unique=True)
    correctName = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.alternateName}"

    def __repr__(self):
        str = "Id: {}, Alternative Name: {}, Corrected Name: {}\n" 
        str =str.format( self.id, self.alternateName, self.correctName)
        return str
