from django.forms import ModelForm
from .models import Trail, Trailhead

class TrailForm(ModelForm):
  class Meta:
    model = Trail
    fields = ['name', 'region', 'coordinates', 'length', 'elevation_gain']

class TrailheadForm(ModelForm):
  class Meta:
    model = Trailhead
    fields = ('trail', 'name', 'coordinates', 'pkg_type', 'pkg_capacity', 'bathroom')