import uuid
from django.db import models

class Trail(models.Model):
  def __str__(self):
    return self.name

  def get_id(self):
    return self.id

  REGION_CHOICES = [
    ('OP', 'Olympic Peninsula'),
    ('NC', 'North Cascades'),
    ('CC', 'Central Cascades'),
    ('SQ', 'Snoqualmie'),
    ('SC', 'South Cascades'),
    ('EW', 'Eastern Washington'),
    ('CW', 'Central Washington'),
    ('WW', 'Western Washington Lowlands'),
    ('SW', 'Southwest Washington'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  modified = models.DateTimeField('time modified', auto_now=True)

  name = models.CharField(max_length=100, unique=True, help_text='Trail Name')
  region = models.CharField(
    max_length=2,
    choices=REGION_CHOICES,
    help_text='Geographic region in Washington where trail is located'
  )
  coordinates = models.CharField(
    max_length=25,
    help_text='Geographic coordinates searchable via Google Maps'
  )
  length = models.DecimalField(
    max_digits=4, decimal_places=1, help_text='From 0.0 to 999.9 miles', blank=True, null=True
  )
  elevation_gain = models.IntegerField('Elevation Gain', 
    blank=True, null=True,
    help_text='From trailhead to highest point of trail'
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
  trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
  modified = models.DateTimeField('time modified', auto_now=True)

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
  pkg_type = models.CharField(
    max_length=2, blank=True, null=True,
    choices=PARKING_TYPES,
    help_text='Type of Parking at Trailhead'
  )
  pkg_capacity = models.IntegerField('Parking Capacity', 
    blank=True, null=True,
    help_text='Approximate number of cars capable of parking at trailhead lot',
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
  trail = models.ForeignKey(Trail, on_delete=models.CASCADE)
  trailhead = models.ForeignKey(Trailhead, on_delete=models.CASCADE)

  created = models.DateTimeField('time created', auto_now_add=True)
  modified = models.DateTimeField('time modified', auto_now=True)

  date_hiked = models.DateField(help_text='What date was the hike?')
  day_hiked = models.CharField(
    max_length=2,
    choices=DAYS,
    help_text='What day of the week was the hike?'
  )
  access = models.CharField(
    max_length=2, blank=True, null=True,
    choices=ACCESS_TYPES,
    help_text='How is the trailhead accessed?'
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
  pkg_location = models.CharField(
    max_length=2,
    choices=PARKING_TYPES,
    help_text='Where did you park at the trailhead?'
  )
  pkg_estimate_begin = models.IntegerField(
    'Percentage Capacity Start',
    help_text='Approximate parking capacity full at trailhead arrival',
  )
  pkg_estimate_end = models.IntegerField(
    'Percentage Capacity End',
    help_text='Approximate parking capacity full at trailhead departure',
  )
  cars_seen = models.IntegerField(
    'Cars seen', help_text='Most cars seen at arrival/departure'
  )
  people_seen = models.IntegerField(
    'People seen', help_text='Approximate number of people encountered on trail'
  )
  horses_seen = models.BooleanField()
  dogs_seen = models.BooleanField()
