from django.forms import ModelForm, SelectDateWidget, Form, ChoiceField
from .models import Trail, Trailhead, Report
from datetime import datetime

class TrailForm(ModelForm):
  class Meta:
    model = Trail
    fields = ['name', 'region', 'coordinates', 'length', 'elevation_gain']

class TrailheadForm(ModelForm):
  class Meta:
    model = Trailhead
    fields = ('trail', 'name', 'coordinates', 'access', 'access_distance', 'pkg_type', 'pkg_capacity', 'bathroom_type', 'bathroom_status')

class ReportForm(ModelForm):
  class Meta:
    year_choices = []
    current_year = datetime.today().year
    for i in range(10):
      year_choices.append(current_year - i)

    model = Report
    fields = ('trail', 'trailhead', 'date_hiked', 'day_hiked', 'weather_type', 'temperature', 'car_type', 'access', 'access_distance', 'access_condition','trail_begin', 'trail_end', 'bathroom_type', 'bathroom_status', 'pkg_location', 'pkg_estimate_begin', 'pkg_estimate_end', 'cars_seen', 'people_seen', 'horses_seen', 'dogs_seen')
    widgets = {
      'date_hiked': SelectDateWidget(
        years=year_choices,
        empty_label=("Year", "Month", "Day")
      ),
    }

class SelectDayForm(Form):
  DAYS = [
    ('', '------'),
    ('M', 'Monday'),
    ('T', 'Tuesday'),
    ('W', 'Wednesday'),
    ('Th', 'Thursday'),
    ('F', 'Friday'),
    ('S', 'Saturday'),
    ('Su', 'Sunday')
  ]

  days_field = ChoiceField(choices = DAYS, label='')

class SelectTimeForm(Form):
  TIME = [
    ('', '------'),
    ('morning', 'Morning'),
    ('afternoon', 'Afternoon'),
    ('evening', 'Evening'),
    ('night', 'Night')
  ]

  time_field = ChoiceField(choices = TIME, label='')
