from django.contrib import admin
from .models import Company, Data, Document, File, Page, Permit, Report, ReportType, State, WellStatus, Well,  WellClass, WellPurpose

# Company.
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name")
admin.site.register(Company, CompanyAdmin)

# Data. 
class DataAdmin(admin.ModelAdmin):
    list_display = ("id", "page")
admin.site.register(Data, DataAdmin)

# Document. 
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "well", "document_name", "report", "status", "url")
    list_filter = ("well", "document_name", "status")
admin.site.register(Document, DocumentAdmin)

# Report. 
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "well", "report_type", "report_name", "gov_report_name", "gov_id", "url")
    list_filter = ("well", "report_type", "report_name")
admin.site.register(Report, ReportAdmin)

# Report Type.
admin.site.register(ReportType)

# File. 
class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "file_ext", "file_location")
admin.site.register(File, FileAdmin)

# Page. 
class PageAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "page_no", "file")
admin.site.register(Page, PageAdmin)

# Permit.
admin.site.register(Permit)

# State.
class StateAdmin(admin.ModelAdmin):
    list_display = ("name_short", "name_long")
admin.site.register(State, StateAdmin)

# WellStatus.
admin.site.register(WellStatus)

# Well Class. 
admin.site.register(WellClass)

# Well Purpose. 
admin.site.register(WellPurpose)

# Well.
class WellAdmin(admin.ModelAdmin):
    list_display = ("id", "well_name", "owner", "state","permit", "status", "well_class", "purpose")
    list_filter = ("well_name", "owner", "state", "permit", "status", "well_class", "purpose")
admin.site.register(Well, WellAdmin)

