from django.test import TestCase
from datetime import datetime

from ..models import Trail, Trailhead, Report
from .mocks import *

class RegionModelTests(TestCase):
  def test_create_region(self):
    region = create_region(name='CC')

    self.assertEqual(region.name, 'CC')
    self.assertIsNotNone(region.id)
    self.assertIsNotNone(region.region_slug)

class TrailModelTests(TestCase):
  # create trail with all required fields returns a trail
  def test_create_trail(self):
    region = create_region(name='CC')
    trail = create_trail(region=region)

    self.assertEqual(trail.region.name, region.name)
    self.assertIsNotNone(trail.coordinates)
    self.assertIsNotNone(trail.trail_slug)
    self.assertIsNone(trail.length_json)
    self.assertFalse(trail.trailheads.all().exists())

class TrailheadModelTests(TestCase):
  # create trailhead for a trail, returns trailhead
  def test_create_trailhead(self):
    region = create_region(name='CC')
    trail = create_trail(region=region)
    trailhead = create_trailhead(trail=trail, region=region, filters=None)

    self.assertTrue(trailhead.trails.all().exists())
    self.assertTrue(trail.trailheads.all().exists())
    self.assertEqual(trailhead.trails.all()[0].name, trail.name)
    self.assertEqual(trailhead.region.name, region.name)
    self.assertIsNotNone(trailhead.trailhead_slug)

class ReportModelTests(TestCase):
  # create report for a trailhead/trail
  def test_create_report(self):
    region = create_region(name='CC')
    trail = create_trail(region=region)
    trailhead = create_trailhead(region=region, trail=trail, filters=None)
    time = datetime.now()

    report = create_report(report={ 
      'region': region, 'trail': trail, 'trailhead': trailhead
    })

    self.assertEqual(report.trailhead.name, trailhead.name)
    self.assertEqual(report.region.name, region.name)
    self.assertEqual(report.trail.name, trail.name)
    self.assertGreater(report.cars_seen, 0)
    self.assertIs(report.trail.name, trail.name)
    self.assertIs(report.trailhead.name, trailhead.name)