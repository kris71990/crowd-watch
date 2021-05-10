from django.forms import ModelForm, TextInput
from .models import Trail, Trailhead, Report

class TrailForm(ModelForm):
  class Meta:
    model = Trail
    fields = ['name', 'region', 'coordinates', 'length', 'elevation_gain']
    # widgets = {
    #   'region': TextInput(attrs={ 'readonly': 'readonly' })
    # }

class TrailheadForm(ModelForm):
  class Meta:
    model = Trailhead
    fields = ('trail', 'name', 'coordinates', 'pkg_type', 'pkg_capacity', 'bathroom')
    # widgets = {
    #   'trail': TextInput(attrs={ 'readonly': 'readonly' })
    # }

class ReportForm(ModelForm):
  class Meta:
    model = Report
    fields = ('trail', 'trailhead', 'date_hiked', 'day_hiked', 'trail_begin', 'trail_end', 'bathroom', 'pkg_estimate_begin', 'pkg_estimate_end', 'cars_seen', 'people_seen', 'horses_seen', 'dogs_seen')