from django.test import TestCase
from django.urls import reverse
from faker import Faker
from datetime import datetime

from ...models import Trail, Trailhead, Report
from ..mocks import *

fake = Faker()

# /<region>/<trail>/reports
# /<region>/<trail>/<trailhead>/reports
class ReportViewTests(TestCase):
  # returns empty list of reports for a trail
  def test_report_list_trail_empty(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region='CC', coordinates=fake.word())
    response = self.client.get(reverse('reports_trail', args=(region, trailhead.trail.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trail'], trailhead.trail)
    self.assertQuerysetEqual(response.context['reports_list'], [])
    
  # returns empty list of reports for a trailhead
  def test_report_list_trailhead_empty(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region='CC', coordinates=fake.word())
    response = self.client.get(reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertQuerysetEqual(response.context['reports_list'], [])

  # returns list of reports for a trailhead in order of most recent
  def test_report_list_trailhead(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region=region, coordinates=fake.word())
    days = ['M', 'T', 'W', 'TH', 'F']

    for i in range(5):
      create_report(report={
        'trail': trailhead.trail, 
        'trailhead': trailhead,
        'date_hiked': fake.date(),
        'day_hiked': days[i],
        'trail_begin': fake.time(),
        'trail_end': fake.time(),
        'bathroom_status': 'C',
        'bathroom_type': 'FP',
        'access': 'FS',
        'pkg_location': 'P',
        'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
        'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
        'cars_seen': fake.pyint(),
        'people_seen': fake.pyint(),
        'horses_seen': fake.boolean(),
        'dogs_seen': fake.boolean()
      })

    response = self.client.get(reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,)))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Reports (5)')
    self.assertEqual(len(reports), 5)
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertEqual(reports[0].trailhead.name, reports[1].trailhead.name)
    self.assertGreater(reports[0].modified, reports[1].modified)
    self.assertGreater(reports[2].modified, reports[3].modified)

  # return list of reports for trail regardless of trailhead, in order
  def test_report_list_trail(self):
    region = 'CC'
    trail = create_trail(name=fake.name(), region=region, coordinates=fake.word())
    days = ['M', 'T', 'W', 'TH', 'F']

    for i in range(2):
      trailhead = create_trailhead(trail=trail, name=fake.name(), coordinates=fake.word())
      create_report(report={
        'trail': trailhead.trail, 
        'trailhead': trailhead,
        'date_hiked': fake.date(),
        'day_hiked': days[i],
        'trail_begin': fake.time(),
        'trail_end': fake.time(),
        'bathroom_status': 'O',
        'bathroom_type': 'FP', 
        'access': 'FS',
        'pkg_location': 'P',
        'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
        'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
        'cars_seen': fake.pyint(),
        'people_seen': fake.pyint(),
        'horses_seen': fake.boolean(),
        'dogs_seen': fake.boolean()
      })

    response = self.client.get(reverse('reports_trail', args=(region, trail.id,)))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Reports (2)')
    self.assertEqual(len(reports), 2)
    self.assertNotEqual(reports[0].trailhead.name, reports[1].trailhead.name)
    self.assertGreater(reports[0].modified, reports[1].modified)

  # creates a report and returns updated list of reports
  def test_create_report_view(self):
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
      'bathroom_status': 'O',
      'bathroom_type': 'FP',
      'access': 'P',
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
    
  def test_single_report(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region=region, coordinates=fake.word())
    time = datetime.now()
    report = create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': fake.time(),
      'bathroom_status': 'O',
      'bathroom_type': 'FP',
      'access': 'P',
      'pkg_location': 'P',
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean()
    })

    response = self.client.get(reverse('report', args=(region, trailhead.trail.id, trailhead.id, report.id,)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('report.html')
    self.assertEqual(response.context['report'].trail_begin, time.time())