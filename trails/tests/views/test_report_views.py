from django.test import TestCase
from django.urls import reverse
from faker import Faker
from datetime import datetime, time

from ..mocks import *

fake = Faker()

# /<region>/<trail>/reports
# /<region>/<trail>/<trailhead>/reports
class ReportViewTests(TestCase):
  def test_report_feed(self):
    regions = ['CC', 'WW', 'NC']
    days = ['M', 'T', 'W', 'TH', 'F']
    for i in range(3):
      trailhead = create_trail_and_trailhead(name=fake.name(), region=regions[i], coordinates=fake.word(), filters=None)
      create_report(report={
        'trail': trailhead.trail, 
        'trailhead': trailhead,
        'date_hiked': fake.date(),
        'day_hiked': days[i],
        'trail_begin': fake.time(),
        'trail_end': fake.time(),
        'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
        'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
        'cars_seen': fake.pyint(),
        'people_seen': fake.pyint(),
        'horses_seen': fake.boolean(),
        'dogs_seen': fake.boolean()
      })
      
    response = self.client.get(reverse('reports_list'))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('report_list.html')
    self.assertContains(response, 'Report Feed')

    self.assertEqual(len(reports), 3)
    self.assertGreater(reports[0].modified, reports[1].modified)
    self.assertGreater(reports[1].modified, reports[2].modified)

  # returns empty list of reports for a trail
  def test_report_list_trail_empty(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region='CC', coordinates=fake.word(), filters=None)
    response = self.client.get(reverse('reports_trail', args=(region, trailhead.trail.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trail'], trailhead.trail)
    self.assertQuerysetEqual(response.context['reports_list'], [])
    
  # returns empty list of reports for a trailhead
  def test_report_list_trailhead_empty(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region='CC', coordinates=fake.word(), filters=None)
    response = self.client.get(reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertQuerysetEqual(response.context['reports_list'], [])

  # returns list of reports for a trailhead in order of most recent
  def test_report_list_trailhead(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region=region, coordinates=fake.word(), filters=None)
    days = ['M', 'T', 'W', 'TH', 'F']

    for i in range(5):
      create_report(report={
        'trail': trailhead.trail, 
        'trailhead': trailhead,
        'date_hiked': fake.date(),
        'day_hiked': days[i],
        'trail_begin': fake.time(),
        'trail_end': fake.time(),
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
      trailhead = create_trailhead(trail=trail, name=fake.name(), coordinates=fake.word(), filters=None)
      create_report(report={
        'trail': trailhead.trail, 
        'trailhead': trailhead,
        'date_hiked': fake.date(),
        'day_hiked': days[i],
        'trail_begin': fake.time(),
        'trail_end': fake.time(),
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
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    post_response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'car_type': 'Suv',
      'weather_type': 'S',
      'temperature': 'C',
      'bathroom_status': 'C',
      'bathroom_type': 'FP',
      'access': 'FS',
      'access_distance': 5.0,
      'access_condition': 'P+',
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

  # test access distance error when value is below 0.1
  def test_create_report_error_access_distance(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'access_distance': -0.1,
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0.1.')
  
  # test error when begin time is invalid
  def test_create_report_error_time_begin(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': '2345',
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Enter a valid time.')
  
  # test error when end time is invalid
  def test_create_report_error_time_end(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': '1235',
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Enter a valid time.')

  # test parking capacity start error when value is below 0
  def test_create_report_error_parking_capacity_start(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': -22,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
      'pkg_estimate_begin': -22,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test parking capacity end error when value is below 0
  def test_create_report_error_parking_capacity_end(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': -34,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test cars seen error when value is below 0
  def test_create_report_error_cars_seen(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': -34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test people seen error when value is below 0
  def test_create_report_error_people_seen(self):
    region = 'CC'
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(name=trail_name, region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()

    path = reverse('reports_trailhead', args=(region, trailhead.trail.id, trailhead.id,))
    response = self.client.post(path, { 
      'trail': trailhead.trail.id, 
      'trailhead': trailhead.id,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': -344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

# <str:region>/<str:trail>/<str:trailhead>/<str:report>/
class SingleReportViewTests(TestCase):
  # renders single report 
  def test_single_report(self):
    region = 'CC'
    trailhead = create_trail_and_trailhead(name=fake.name(), region=region, coordinates=fake.word(), filters=None)
    time = datetime.now()
    report = create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'trail_begin': time.time(),
      'trail_end': fake.time(),
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

# reports/<str:day>
# reports/<str:time>
# <trail>/reports/<day>
# <trail>/reports/<time>
class ReportFilterViews(TestCase):
  # returns reports from all trails/regions for a specific day
  def test_filter_by_day(self):
    create_bulk_reports('CC', 3)
    create_bulk_reports('NC', 3)
    day = 'S'

    response = self.client.get(reverse('reports_day', args=(day,)))

    reports_day = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports_day.html')

    if reports_day:
      for i in range(len(reports_day)):
        self.assertEqual(reports_day[i].day_hiked, 'S')
    else:
      self.assertContains(response, 'No reports found')

  # returns reports from a trail for a specific day
  def test_filter_by_day_trail(self):
    create_bulk_reports('CC', 2)
    trailhead = create_trail_and_trailhead('sfdsf', 'NC', '342323', None)
    create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'trail_begin': fake.time(),
      'trail_end': fake.time(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'day_hiked': 'S'
    })

    response = self.client.get(reverse('reports_trail_day', args=('NC', trailhead.trail.id, 'S',)))

    reports_day = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertEqual(len(reports_day), 1)
    self.assertEqual(reports_day[0].day_hiked, 'S')

  def test_filter_by_day_trail_empty(self):
    trailhead = create_trail_and_trailhead('test', 'NC', '34223', None)
    create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'trail_begin': fake.time(),
      'trail_end': fake.time(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'day_hiked': 'Th'
    })

    response = self.client.get(reverse('reports_trail_day', args=('NC', trailhead.trail.id, 'S',)))

    trail = response.context['trail_day_empty']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertEqual(trail.name, trailhead.trail.name)
    self.assertContains(response, 'No reports found')

  # returns reports from all trails/regions for a time range
  def test_filter_by_time(self):
    create_bulk_reports('CC', 3)
    create_bulk_reports('NC', 3)
    period = 'morning'
    time_end = time(12, 00)
    time_begin = time(0, 00)

    response = self.client.get(reverse('reports_time', args=(period,)))

    reports_time = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports_time.html')

    if reports_time:
      for i in range(len(reports_time)):
        self.assertLess(reports_time[i].trail_begin, time_end)
        self.assertGreater(reports_time[i].trail_begin, time_begin)
    else:
      self.assertContains(response, 'No reports found')

  # returns reports from a trail for a specific time
  def test_filter_by_time_trail(self):
    trailhead = create_trail_and_trailhead('test', 'NC', '342323', None)
    create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'trail_begin': fake.time(),
      'trail_end': fake.time(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'trail_begin': time(6, 00),
      'trail_end': time(10, 00)
    })

    response = self.client.get(reverse('reports_trail_time', args=('NC', trailhead.trail.id, 'morning',)))

    reports_time = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertEqual(len(reports_time), 1)
    self.assertGreater(reports_time[0].trail_begin, time(0, 00))
    self.assertLess(reports_time[0].trail_begin, time(12, 00))

  def test_filter_by_time_trail_empty(self):
    trailhead = create_trail_and_trailhead('test', 'NC', '34223', None)
    create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'trail_begin': fake.time(),
      'trail_end': fake.time(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'trail_begin': time(13, 00),
      'trail_end': time(16, 00)
    })

    response = self.client.get(reverse('reports_trail_time', args=('NC', trailhead.trail.id, 'morning',)))

    trail = response.context['trail_time_empty']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertEqual(trail.name, trailhead.trail.name)
    self.assertContains(response, 'No reports found')
  