import uuid
from django.db import models

class Trail(models.Model):
  REGION_CHOICES = [
    ('OP', 'Olympic Peninsula'),
    ('NC', 'North Cascades'),
    ('CC', 'Central Cascades'),
    ('SQ', 'Snoqualmie'),
    ('SC', 'South Cascades'),
    ('EW', 'Eastern Washington'),
    ('CW', 'Central Washington'),
    ('WWL', 'Western Washington Lowlands'),
    ('SW', 'Southwest Washington'),
  ]

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100, unique=True)
  region = models.CharField(
    max_length=2,
    choices=REGION_CHOICES,
  )
  coordinates = models.CharField(
    max_length=25
    help_text="Geographic coordinates searchable via Google Maps"
  )
  length = models.DecimalField(
    max_digits=4, decimal_places=1, help_text="From 0.0 to 999.9 miles"
  )
  elevation_gain = models.IntegerField("Elevation Gain", blank=True)

class Trailhead(models.Model):

class Report(models.Model):


