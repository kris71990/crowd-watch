from django.test import TestCase
from datetime import datetime

from ..models import Trail, Trailhead, Report

def create_trail(name, region, coordinates):
  return Trail.objects.create(name=name, region=region, coordinates=coordinates)

def create_trailhead(trail, name, coordinates):
  return Trailhead.objects.create(trail=trail, name=name, coordinates=coordinates)

def create_report(report):
  return Report.objects.create(
    trail=report['trail'], trailhead=report['trailhead'], date_hiked=report['date_hiked'], day_hiked=report['day_hiked'], trail_begin=report['trail_begin'], trail_end=report['trail_end'], bathroom=report['bathroom'], pkg_location=report['pkg_location'], pkg_estimate_begin=report['pkg_estimate_begin'], pkg_estimate_end=report['pkg_estimate_end'], cars_seen=report['cars_seen'], people_seen=report['people_seen'], horses_seen=report['horses_seen'], dogs_seen=report['dogs_seen']
  )


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
      'trail': trail, 'trailhead': trailhead, 'date_hiked': time.date(), 'day_hiked': 'Th', 'trail_begin': time.time(), 'trail_end': time.time(), 'bathroom': 'N', 'pkg_location': 'P', 'pkg_estimate_begin': 15, 'pkg_estimate_end': 50, 'cars_seen': 30, 'people_seen': 100, 'horses_seen': False, 'dogs_seen': True
    })

    self.assertIs(report.cars_seen, 30)
    self.assertIs(report.trail.name, 'test_name')
    self.assertIs(report.trailhead.name, 'th')