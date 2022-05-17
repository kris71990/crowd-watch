from django.core import validators
from django.db import models
from django.urls import reverse
import uuid
from django.core.validators import MinValueValidator

class Region(models.Model):
  def __str__(self):
    return self.name

  REGION_CHOICES = [
    ('OP', 'Olympic Peninsula'),
    ('NC', 'North Cascades'),
    ('CC', 'Central Cascades'),
    ('SQ', 'Snoqualmie'),
    ('SC', 'South Cascades'),
    ('WW', 'Western Washington Lowlands'),
    ('EW', 'Eastern Washington'),
    ('CW', 'Central Washington'),
    ('SW', 'Southwest Washington'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(
    choices=REGION_CHOICES,
    max_length=2, 
    unique=True, 
    help_text='Region Name'
  )
  region_slug = models.SlugField(null=True)

class Trail(models.Model):
  def __str__(self):
    return self.name

  def get_id(self):
    return self.id

  region = models.ForeignKey(Region, on_delete=models.CASCADE)
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  modified = models.DateTimeField('time modified', auto_now=True)
  trail_slug = models.SlugField(null=True)

  name = models.CharField(max_length=100, unique=True, help_text='Trail Name')
  coordinates = models.CharField(
    max_length=25,
    help_text='Geographic coordinates searchable via Google Maps'
  )
  length_json = models.JSONField('Trail length', blank=True, null=True,
    help_text='From 0.1 to 999.9 miles'
  )
  elevation_gain_json = models.JSONField('Elevation Gain', blank=True, null=True,
    help_text='From trailhead to highest point of trail',
  )

class Trailhead(models.Model):
  def __str__(self):
    return self.name

  PARKING_TYPES = [
    ('UL', 'Unpaved Lot'),
    ('PL', 'Paved Lot'),
    ('S', 'Street/Road'),
    ('P', 'Designated Pullout/Shoulder')
  ]

  ACCESS_TYPES = [
    ('FS', 'Forest Service Road'),
    ('P', 'Paved Road'),
  ]

  BATHROOM_STATUS = [
    ('O', 'Open'),
    ('C', 'Closed'),
  ]

  BATHROOM_TYPE = [
    ('P', 'Portable/Outhouse'),
    ('FP', 'Fixed Building, Pit'),
    ('FR', 'Fixed Building with plumbing')
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  region = models.ForeignKey(Region, on_delete=models.CASCADE)
  trails = models.ManyToManyField(Trail, related_name='trailheads')
  modified = models.DateTimeField('time modified', auto_now=True)
  trailhead_slug = models.SlugField(null=True)

  name = models.CharField(max_length=50, unique=True, help_text='Name of Trailhead')
  coordinates = models.CharField(
    max_length=25,
    help_text='Geographic coordinates searchable via Google Maps'
  )

  access = models.CharField(
    max_length=2, blank=True, null=True,
    choices=ACCESS_TYPES,
    help_text='How is the trailhead accessed?'
  )
  access_distance = models.IntegerField(
    blank=True, null=True,
    help_text='If accessed via service road, length of service road from paved road to trailhead',
    validators=[MinValueValidator(0.1)]
  )
  pkg_type = models.CharField('Parking type',
    max_length=2, blank=True, null=True,
    choices=PARKING_TYPES,
    help_text='Type of Parking at Trailhead'
  )
  pkg_capacity = models.IntegerField('Parking capacity', 
    blank=True, null=True,
    help_text='Approximate number of cars capable of parking at trailhead lot',
    validators=[MinValueValidator(0)]
  )
  bathroom_type = models.CharField(
    blank=True, null=True,
    max_length=2, 
    choices=BATHROOM_TYPE,
    help_text='Is there a bathroom at the trailhead?'
  )
  bathroom_status = models.CharField(
    blank=True, null=True,
    max_length=1, 
    choices=BATHROOM_STATUS,
    help_text='Is the bathroom open?'
  )

class Report(models.Model):
  def __str__(self):
    return str(self.modified)

  def get_trailhead(self):
    return self.trailhead.name
  
  def get_trail(self):
    return self.trail.name

  PARKING_TYPES = [
    ('UL', 'Unpaved Lot'),
    ('PL', 'Paved Lot'),
    ('S', 'Street/Road'),
    ('P', 'Designated Pullout/Shoulder')
  ]

  DAYS = [
    ('M', 'Monday'),
    ('T', 'Tuesday'),
    ('W', 'Wednesday'),
    ('Th', 'Thursday'),
    ('F', 'Friday'),
    ('S', 'Saturday'),
    ('Su', 'Sunday')
  ]

  CAR_TYPES = [
    ('Suv', 'SUV'),
    ('S', 'Sedan'),
    ('T', 'Truck'),
    ('4wd', 'Four-wheel drive')
  ]

  ACCESS_TYPES = [
    ('FS', 'Forest Service Road'),
    ('P', 'Paved Road'),
  ]

  ACCESS_CONDITIONS = [
    ('I', 'Impassable'),
    ('P+', 'Many potholes'),
    ('P', 'Potholes'),
    ('P-', 'Occasional potholes'),
    ('G', 'Good')
  ]

  BATHROOM_STATUS = [
    ('O', 'Open'),
    ('C', 'Closed'),
  ]

  BATHROOM_TYPE = [
    ('P', 'Portable/Outhouse'),
    ('FP', 'Fixed Building, Pit'),
    ('FR', 'Fixed Building with plumbing')
  ]

  WEATHER_TYPE = [
    ('R', 'Rain'),
    ('Sn', 'Snow'),
    ('S', 'Sun'),
    ('PC', 'Partly Cloudy'),
    ('O', 'Overcast')
  ]

  TEMPERATURES = [
    ('F', '< 32'),
    ('C', '33-50'),
    ('N', '51-70'),
    ('W', '71-85'),
    ('H', '86-100'),
    ('E', '100 <')
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
  trailhead = models.ForeignKey(Trailhead, on_delete=models.CASCADE)
  region = models.ForeignKey(Region, on_delete=models.CASCADE)

  created = models.DateTimeField('time created', auto_now_add=True)
  modified = models.DateTimeField('time modified', auto_now=True)

  length = models.DecimalField(
    max_digits=4, decimal_places=1, help_text='From 0.1 to 999.9 miles', blank=True, null=True,
    validators=[MinValueValidator(0.1)]
  )
  elevation_gain = models.IntegerField('Elevation Gain', 
    blank=True, null=True,
    help_text='From trailhead to highest point of trail',
    validators=[MinValueValidator(0)]
  )

  date_hiked = models.DateField(help_text='What date was the hike?')
  day_hiked = models.CharField(
    max_length=2,
    choices=DAYS,
    help_text='What day of the week was the hike?'
  )
  weather_type = models.CharField(
    max_length=2, blank=True, null=True,
    choices=WEATHER_TYPE,
    help_text='What was the weather like?'
  )
  temperature = models.CharField(
    blank=True, null=True,
    max_length=1,
    choices=TEMPERATURES,
    help_text='What was the temperature?'
  )
  car_type = models.CharField(
    max_length=3, blank=True, null=True,
    choices=CAR_TYPES,
    help_text='With what type of car did you access the trail?'
  )
  access = models.CharField(
    max_length=2, blank=True, null=True,
    choices=ACCESS_TYPES,
    help_text='How is the trailhead accessed?'
  )
  access_distance = models.DecimalField(
    max_digits=3, decimal_places=1,
    blank=True, null=True,
    help_text='If accessed via service road, length of service road from paved road to trailhead',
    validators=[MinValueValidator(0.1)]
  )
  access_condition = models.CharField(
    blank=True, null=True,
    max_length=2,
    choices=ACCESS_CONDITIONS,
    help_text='If accessed via service road, the condition of the service road?'
  )
  trail_begin = models.TimeField(help_text='What time did the hike begin?')
  trail_end = models.TimeField(help_text='What time did the hike end?')
  bathroom_type = models.CharField(
    blank=True, null=True,
    max_length=2, 
    choices=BATHROOM_TYPE,
    help_text='Is there a bathroom at the trailhead?'
  )
  bathroom_status = models.CharField(
    blank=True, null=True,
    max_length=1, 
    choices=BATHROOM_STATUS,
    help_text='Is the bathroom open?'
  )
  pkg_location = models.CharField('Type of Parking',
    max_length=2,
    choices=PARKING_TYPES,
    help_text='Where did you park at the trailhead?'
  )
  pkg_estimate_begin = models.IntegerField(
    'Percentage Capacity Start',
    help_text='Approximate parking capacity full at trailhead arrival',
    validators=[MinValueValidator(0)]
  )
  pkg_estimate_end = models.IntegerField(
    'Percentage Capacity End',
    help_text='Approximate parking capacity full at trailhead departure',
    validators=[MinValueValidator(0)]
  )
  cars_seen = models.IntegerField(
    'Cars seen', help_text='Most cars seen at arrival/departure',
    validators=[MinValueValidator(0)]
  )
  people_seen = models.IntegerField(
    'People seen', help_text='Approximate number of people encountered on trail',
    validators=[MinValueValidator(0)]
  )
  horses_seen = models.BooleanField()
  dogs_seen = models.BooleanField()
