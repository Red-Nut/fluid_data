from django import forms
from .models import Company, State, WellStatus, WellClass, WellPurpose

class WellFilter(forms.Form):
    well_name = forms.CharField(label='Well', max_length=255, required=False)
    owner = forms.ModelChoiceField(queryset=Company.objects.all().order_by("company_name"), initial=0, required=False)
    state = forms.ModelChoiceField(queryset=State.objects.all().order_by("name_short"), initial=0, required=False)
    permit = forms.CharField(label='Permit', max_length=20, required=False)
    status = forms.ModelChoiceField(queryset=WellStatus.objects.all().order_by("status_name"), initial=0, required=False)
    wellClass = forms.ModelChoiceField(queryset=WellClass.objects.all().order_by("class_name"), initial=0, required=False)
    purpose = forms.ModelChoiceField(queryset=WellPurpose.objects.all().order_by("purpose_name"), initial=0, required=False)
    lat_min = forms.IntegerField(required=False)
    lat_max = forms.IntegerField(required=False)
    long_min = forms.IntegerField(required=False)
    long_max = forms.IntegerField(required=False)
    rig_release_start = forms.DateField(widget=forms.SelectDateWidget,required=False)
    rig_release_end = forms.DateField(widget=forms.SelectDateWidget,required=False)
    orderBy = forms.CharField(widget=forms.HiddenInput(), required=False)
    page = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    show_qty = forms.IntegerField(widget=forms.HiddenInput(), required=False)