from django.test import TestCase
from datetime import datetime

from ..models import Trail, Trailhead, Report
from .mocks import *

class TrailModelTests(TestCase):
  # create trail with all required fields returns a trail
  def test_create_trail(self):
    trail = create_trail(name='test_name', region='CC', coordinates='-23.44, -11.44')
    self.assertIs(trail.name, 'test_name')
    self.assertIs(trail.region, 'CC')
    self.assertIs(trail.coordinates, '-23.44, -11.44')

class TrailheadModelTests(TestCase):
  # create trailhead for a trail, returns trailhead
  def test_create_trailhead(self):
    trail = create_trail(name='test_name', region='CC', coordinates='4352')
    trailhead = create_trailhead(trail=trail, name='th', coordinates='4535')
    self.assertIs(trailhead.name, 'th')
    self.assertIs(trailhead.trail.name, 'test_name')

class ReportModelTests(TestCase):
  # create report for a trailhead/trail
  def test_create_report(self):
    trail = create_trail(name='test_name', region='CC', coordinates='4352')
    trailhead = create_trailhead(trail=trail, name='th', coordinates='4535')
    time = datetime.now()

    report = create_report(report={ 
      'trail': trail, 'trailhead': trailhead, 'date_hiked': time.date(), 'day_hiked': 'Th', 'trail_begin': time.time(), 'trail_end': time.time(), 'car_type': 'Suv', 'temperature': 'W', 'weather_type': 'S', 'access': 'P', 'access_distance': 5.0, 'access_condition': 'P+', 'bathroom_status': 'O', 'bathroom_type': 'FP', 'pkg_location': 'P', 'pkg_estimate_begin': 15, 'pkg_estimate_end': 50, 'cars_seen': 30, 'people_seen': 100, 'horses_seen': False, 'dogs_seen': True
    })

    self.assertIs(report.cars_seen, 30)
    self.assertIs(report.trail.name, 'test_name')
    self.assertIs(report.trailhead.name, 'th')