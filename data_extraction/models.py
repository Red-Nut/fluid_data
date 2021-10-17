from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy  as _

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
    modified = models.DateTimeField(null=True, blank=True)

    def __str__(self):
	    return f"{self.well_name}"

    def __repr__(self):
        str = "Id: {}, name: {}\n" 
        str =str.format( self.id, self.well_name)
        return str

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
        on_delete=models.CASCADE,
        related_name="reports"
    )
    url = models.TextField(max_length=1000,null=True)

    def __str__(self):
	    return f"{self.report_name}"

class Document(CreatedModifiedModel):
    MISSING = 1
    DOWNLOADED = 2
    IGNORED = 3
    STATUS = (
        (MISSING, _('Missing')),
        (DOWNLOADED, _('Downloaded')),
        (IGNORED, _('Ignored')),
    )
    
    document_name = models.CharField(max_length=255)
    well = models.ForeignKey(
        Well,
        on_delete=models.CASCADE,
        related_name="documents"
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
    converted = models.BooleanField(default=False)

    def __str__(self):
	    return f"{self.document_name}"

    def __repr__(self):
        str = "Id: {}, well_id: {}, name: {}, file_id: {}\n" 
        str =str.format( self.id, self.well.id, self.company_name, self.file.id)
        return str

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

    def __str__(self):
	    return f"({self.x},{self.y}) {self.text.text}"

 # ***************************** Data  ***************************** 

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







