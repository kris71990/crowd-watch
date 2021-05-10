from django.test import TestCase
from django.urls import reverse
from faker import Faker

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
    