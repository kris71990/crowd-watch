from django.test import TestCase
from django.urls import reverse
from faker import Faker
from datetime import datetime

from ...models import Trail, Trailhead, Report
from ..mocks import *

fake = Faker()

class ReportViewTests(TestCase):
  def test_report_list_trail_empty(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region='CC', coordinates=fake.word())
    response = self.client.get(reverse('reports_trail', args=(region, trailhead.trail.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trail'], trailhead.trail)
    self.assertQuerysetEqual(response.context['reports_list'], [])
    
  def test_report_list_trailhead_empty(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region='CC', coordinates=fake.word())
    response = self.client.get(reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertQuerysetEqual(response.context['reports_list'], [])

  def test_create_report(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word())
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    post_response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'bathroom': 'N',
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
      'horses_seen': False,
      'dogs_seen': True
    })

    self.assertRedirects(post_response, path)
    get_response = self.client.get(path, args=(region, trailhead.trail.id, trailhead.id,))
    reports = get_response.context['reports_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(get_response, 'Reports (1)')
    self.assertEqual(len(reports), 1)
    self.assertEqual(reports[0].trail.name, 'test_trail')
    