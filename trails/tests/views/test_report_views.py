from django.test import TestCase
from django.urls import reverse
from faker import Faker
from datetime import datetime, time
from decimal import Decimal

from ..mocks import *

fake = Faker()

# /<region>/<trail>/reports
# /<region>/<trail>/<trailhead>/reports
class ReportViewTests(TestCase):
  def test_report_feed(self):
    regions = ['CC', 'WW', 'NC']
    days = ['M', 'T', 'W']
    for i in range(3):
      region = create_region(regions[i])
      trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
      create_report(report={
        'region': region,
        'trail': trailhead.trails.all()[0], 
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
    self.assertGreater(reports[0].date_hiked, reports[1].date_hiked)
    self.assertGreater(reports[1].date_hiked, reports[2].date_hiked)

  # returns empty list of reports for a trail
  def test_report_list_trail_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    trailhead_trails = trailhead.trails.all()
    response = self.client.get(reverse('reports_trail', args=(region.region_slug, trailhead_trails[0].trail_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trail'], trailhead_trails[0])
    self.assertQuerysetEqual(response.context['reports_list'], [])
    
  # returns empty list of reports for a trailhead
  def test_report_list_trailhead_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    trailhead_trails = trailhead.trails.all()
    response = self.client.get(reverse('reports_trailhead', args=(region.region_slug, trailhead.trailhead_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports_trailhead.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertQuerysetEqual(response.context['reports_list'], [])

  # returns list of reports for a trailhead in order of most recent
  def test_report_list_trailhead(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    trailhead_trails = trailhead.trails.all()
    days = ['M', 'T', 'W', 'TH', 'F']

    for i in range(5):
      create_report(report={
        'region': region,
        'trail': trailhead_trails[0], 
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

    response = self.client.get(reverse('reports_trailhead', args=(region.region_slug, trailhead.trailhead_slug,)))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports_trailhead.html')
    self.assertContains(response, 'Reports (5)')
    self.assertEqual(len(reports), 5)
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertEqual(reports[0].trailhead.name, reports[1].trailhead.name)
    self.assertGreater(reports[0].date_hiked, reports[1].date_hiked)
    self.assertGreater(reports[2].date_hiked, reports[3].date_hiked)

  # return list of reports for trail regardless of trailhead, in order
  def test_report_list_trail(self):
    region = create_region('CC')
    trail = create_trail(region=region, name=fake.name())
    days = ['M', 'T']

    for i in range(2):
      trailhead = create_trailhead(region=region, trail=trail, name=fake.name(), filters=None)
      create_report(report={
        'region': region,
        'trail': trailhead.trails.all()[0], 
        'trailhead': trailhead,
        'date_hiked': fake.date(),
        'day_hiked': days[i],
        'trail_begin': fake.time(),
        'trail_end': fake.time(),
        'pkg_location': 'S',
        'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
        'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
        'cars_seen': fake.pyint(),
        'people_seen': fake.pyint(),
        'horses_seen': fake.boolean(),
        'dogs_seen': fake.boolean()
      })

    response = self.client.get(reverse('reports_trail', args=(region.region_slug, trail.trail_slug,)))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('reports.html')
    self.assertContains(response, 'Reports (2)')
    self.assertEqual(len(reports), 2)
    self.assertNotEqual(reports[0].trailhead.name, reports[1].trailhead.name)
    self.assertGreater(reports[0].date_hiked, reports[1].date_hiked)

  # creates a report and returns updated list of reports
  def test_create_report_view(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    post_response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
      'day_hiked': 'M',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': 29,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertRedirects(post_response, path)
    get_response = self.client.get(path, args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    reports = get_response.context['reports_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(get_response, 'Reports (1)')
    self.assertEqual(len(reports), 1)
    self.assertEqual(reports[0].trail.name, trailhead_trails[0].name)

  # test access distance error when value is below 0.1
  def test_create_report_error_access_distance(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0.1.')
  
  # test error when begin time is invalid
  def test_create_report_error_time_begin(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Enter a valid time.')
  
  # test error when end time is invalid
  def test_create_report_error_time_end(self):
    region = create_region('CC')
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Enter a valid time.')

  # test parking capacity start error when value is below 0
  def test_create_report_error_parking_capacity_start(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test parking capacity end error when value is below 0
  def test_create_report_error_parking_capacity_end(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test cars seen error when value is below 0
  def test_create_report_error_cars_seen(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test people seen error when value is below 0
  def test_create_report_error_people_seen(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked_day': 1,
      'date_hiked_month': 1,
      'date_hiked_year': 2020,
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
    self.assertTemplateUsed('reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

# <str:region>/<str:trail>/<str:trailhead>/<str:report>/
class SingleReportViewTests(TestCase):
  # renders single report 
  def test_single_report(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    report = create_report(report={
      'region': region,
      'trail': trailhead_trails[0], 
      'trailhead': trailhead,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked': time.date(),
      'day_hiked': 'Th',
      'trail_begin': time.time(),
      'trail_end': time.time(),
      'pkg_location': 'P',
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'dogs_seen': fake.boolean(),
      'horses_seen': fake.boolean(),
    })

    response = self.client.get(reverse('report', args=(region, trailhead_trails[0].trail_slug, trailhead.trailhead_slug, report.id,)))
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
    region = create_region('NC')
    create_bulk_reports(region, 3)
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
    north = create_region('NC')
    central = create_region('CC')
    create_bulk_reports(central, 3)
    trailhead = create_trail_and_trailhead(region=central, name=fake.name(), filters=None)

    create_report(report={
      'region': north,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'length': 5.4,
      'elevation_gain': 500,
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

    response = self.client.get(reverse('reports_trail_day', args=(north.region_slug, trailhead.trails.all()[0].trail_slug, 'S',)))

    reports_day = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(len(reports_day), 1)
    self.assertEqual(reports_day[0].day_hiked, 'S')

  def test_filter_by_day_trail_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    trailhead_trail = trailhead.trails.all()[0]
    create_report(report={
      'region': region,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'length': 5.4,
      'elevation_gain': 500,
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

    response = self.client.get(reverse('reports_trail_day', args=(region.region_slug, trailhead_trail.trail_slug, 'S',)))

    trail = response.context['trail']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(trail.name, trailhead_trail.name)
    self.assertContains(response, 'No reports found')

  # returns reports from all trails/regions for a time range
  def test_filter_by_time(self):
    central = create_region('CC')
    north = create_region('NC')
    create_bulk_reports(central, 3)
    create_bulk_reports(north, 3)
    period = 'early morning'
    time_begin = time(4, 00)
    time_end = time(6, 59)

    response = self.client.get(reverse('reports_time', args=(period,)))

    reports_time = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_time.html')

    if reports_time:
      for i in range(len(reports_time)):
        self.assertLess(reports_time[i].trail_begin, time_end)
        self.assertGreater(reports_time[i].trail_begin, time_begin)
    else:
      self.assertContains(response, 'No reports found')

  # returns reports from a trail for a specific time
  def test_filter_by_time_trail(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    trailhead_trail = trailhead.trails.all()[0]

    create_report(report={
      'region': region,
      'trail': trailhead_trail, 
      'trailhead': trailhead,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked': fake.date(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'day_hiked': 'Th',
      'trail_begin': time(6, 00),
      'trail_end': time(10, 00)
    })

    create_report(report={
      'region': region,
      'trail': trailhead_trail, 
      'trailhead': trailhead,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked': fake.date(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'day_hiked': 'Th',
      'trail_begin': time(7, 00),
      'trail_end': time(10, 00)
    })

    response = self.client.get(reverse('reports_trail_time', args=(region.region_slug, trailhead_trail.trail_slug, 'early morning',)))

    reports_time = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(len(reports_time), 1)
    self.assertEqual(reports_time[0].trail, trailhead_trail)
    self.assertGreater(reports_time[0].trail_begin, time(4, 00))
    self.assertLess(reports_time[0].trail_begin, time(6, 59))

  def test_filter_by_time_trail_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    create_report(report={
      'region': region,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'length': 5.4,
      'elevation_gain': 500,
      'date_hiked': fake.date(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'day_hiked': 'Th',
      'trail_begin': time(13, 00),
      'trail_end': time(16, 00)
    })

    response = self.client.get(reverse('reports_trail_time', args=(region.region_slug, trailhead.trails.all()[0].trail_slug, 'early morning',)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(response.context['trail'].name, trailhead.trails.all()[0].name)
    self.assertEqual(response.context['reports_total'], 1)
    self.assertContains(response, 'No reports found')
  