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
    url = models.TextField(max_length=1000,null=True, blank=True)

    def __str__(self):
	    return f"{self.report_name}"

class DataType(CreatedModifiedModel):
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type_name}"

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
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=1,
    )
    converted = models.BooleanField(default=False, null=True)
    conversion_status = models.PositiveSmallIntegerField(
        choices=CONVERSION,
        default=1,
    )

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
            link = settings.MEDIA_URL + 'well_data/' + self.file.file_location + self.file.file_name + '.' + self.file.file_ext.replace(".","")

        return link

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

class DataType(CreatedModifiedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
	    return f"{self.name}"

class ExtractionMethod(CreatedModifiedModel):
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(
        Unit,
        null=False,
        on_delete=models.RESTRICT
    ) 
    data_type = models.ForeignKey(
        Unit,
        null=False,
        on_delete=models.RESTRICT
    ) 

    def __str__(self):
	    return f"{self.name}"

class ExtractionAction(CreatedModifiedModel):
    INITIAL = 0
    NEXT=2
    SEARCH=2
    TYPE = (
        (INITIAL, _('Initial Action')),
        (NEXT, _('Immediately Next Text')),
        (SEARCH, _('Find Text')),
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

    type = models.PositiveSmallIntegerField(
        choices=TYPE,
    )
    direction = models.PositiveSmallIntegerField(
        choices=DIRECTION,
    )

class ExtractionActions(CreatedModifiedModel):
    method = models.ForeignKey(
        ExtractionMethod,
        null=False,
        on_delete=models.CASCADE,
        related_name="actions"
    ) 
    action = models.ForeignKey(
        ExtractionAction,
        null=False,
        on_delete=models.CASCADE
    ) 
    
    order = models.IntegerField()

class Data(CreatedModifiedModel):
    page = models.ForeignKey(
        Page,
        null=False,
        on_delete=models.CASCADE,
        related_name="datas"
    ) 
    extraction_method = models.IntegerField()

    def __str__(self):
        return f"{self.page}"

    def __repr__(self):
        str = "Id: {}, page id: {}\n" 
        str =str.format( self.id, self.page)
        return str







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
