from django.test import TestCase
from django.urls import reverse
from datetime import datetime, time

from ..mocks import *

# /<region>/<trail>/reports
# /<region>/<trail>/<trailhead>/reports
class ReportViewTests(TestCase):
  def test_report_feed(self):
    regions = ['CC', 'WW', 'NC']
    for i in range(3):
      region = create_region(regions[i])
      trailhead = create_trail_and_trailhead(region=region, filters=None)
      create_report(report={
        'region': region,
        'trail': trailhead.trails.all()[0], 
        'trailhead': trailhead,
      })
      
    response = self.client.get(reverse('reports_list'))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/report_list.html')
    self.assertContains(response, 'Report Feed')

    self.assertEqual(len(reports), 3)
    self.assertGreater(reports[0].date_hiked, reports[1].date_hiked)
    self.assertGreater(reports[1].date_hiked, reports[2].date_hiked)

  # returns empty list of reports for a trail
  def test_report_list_trail_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    trailhead_trails = trailhead.trails.all()
    response = self.client.get(reverse('reports_trail', args=(region.region_slug, trailhead_trails[0].trail_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trail'], trailhead_trails[0])
    self.assertQuerysetEqual(response.context['reports_list'], [])
    
  # returns empty list of reports for a trailhead
  def test_report_list_trailhead_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    trailhead_trails = trailhead.trails.all()
    response = self.client.get(reverse('reports_trailhead', args=(region.region_slug, trailhead.trailhead_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trailhead.html')
    self.assertContains(response, 'No reports found')
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertQuerysetEqual(response.context['reports_list'], [])

  # returns list of reports for a trailhead in order of most recent
  def test_report_list_trailhead(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    trailhead_trails = trailhead.trails.all()
    days = ['M', 'T', 'W', 'TH', 'F']

    for i in range(5):
      create_report(report={
        'region': region,
        'trail': trailhead_trails[0], 
        'trailhead': trailhead,
        'day_hiked': days[i],
      })

    response = self.client.get(reverse('reports_trailhead', args=(region.region_slug, trailhead.trailhead_slug,)))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trailhead.html')
    self.assertContains(response, 'Reports (5)')
    self.assertEqual(len(reports), 5)
    self.assertEqual(response.context['trailhead'], trailhead)
    self.assertEqual(reports[0].trailhead.name, reports[1].trailhead.name)
    self.assertGreater(reports[0].date_hiked, reports[1].date_hiked)
    self.assertGreater(reports[2].date_hiked, reports[3].date_hiked)

  # return list of reports for trail regardless of trailhead, in order
  def test_report_list_trail(self):
    region = create_region('CC')
    trail = create_trail(region=region)
    days = ['M', 'T']

    for i in range(2):
      trailhead = create_trailhead(region=region, trail=trail, filters=None)
      create_report(report={
        'region': region,
        'trail': trailhead.trails.all()[0], 
        'trailhead': trailhead,
        'day_hiked': days[i],
      })

    response = self.client.get(reverse('reports_trail', args=(region.region_slug, trail.trail_slug,)))
    reports = response.context['reports_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertContains(response, 'Reports (2)')
    self.assertEqual(len(reports), 2)
    self.assertNotEqual(reports[0].trailhead.name, reports[1].trailhead.name)
    self.assertGreater(reports[0].date_hiked, reports[1].date_hiked)

  # creates a report and returns updated list of reports
  # also tests update of trail length and elevation gain via update functions upon trail post
  def test_create_report_view(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    create_bulk_reports(region, trail, trailhead, 3)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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
    get_response = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    reports = get_response.context['reports_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed(get_response, 'trails/reports_trail_trailhead.html')
    self.assertContains(get_response, 'Reports (4)')
    self.assertEqual(len(reports), 4)
    self.assertEqual(reports[0].trail.name, trail.name)
    self.assertGreaterEqual(reports[0].date_hiked, reports[1].date_hiked)
    self.assertGreaterEqual(reports[1].date_hiked, reports[2].date_hiked)
    self.assertEqual(get_response.context['trail'].length_json[get_response.context['trailhead'].name], '5.4')
    self.assertEqual(get_response.context['trail'].elevation_gain_json[get_response.context['trailhead'].name], 500)

class ReportViewUpdateTrailTests(TestCase):
  # test that trail update function correctly updates trail and elevation data upwards when new data is within reasonable margin
  def test_create_report_view_update_trail_increase(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response_one = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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

    self.assertRedirects(post_response_one, path)
    get_response_one = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    self.assertEqual(get_response_one.context['trail'].length_json[get_response_one.context['trailhead'].name], '5.4')
    self.assertEqual(get_response_one.context['trail'].elevation_gain_json[get_response_one.context['trailhead'].name], 500)

    post_response_two = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
      'length': 6.4,
      'elevation_gain': 600,
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

    self.assertRedirects(post_response_two, path)
    get_response_two = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response_two.status_code, 200)
    self.assertTemplateUsed(get_response_two, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response_two.context['reports_list']), 2)
    self.assertEqual(get_response_two.context['trail'].length_json[get_response_two.context['trailhead'].name], '5.9')
    self.assertEqual(get_response_two.context['trail'].elevation_gain_json[get_response_two.context['trailhead'].name], 550)

  # test that trail update function correctly updates trail and elevation data downwards when new data is within reasonable margin  
  def test_create_report_view_update_trail_decrease(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response_one = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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

    self.assertRedirects(post_response_one, path)
    get_response_one = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    self.assertEqual(get_response_one.context['trail'].length_json[get_response_one.context['trailhead'].name], '5.4')
    self.assertEqual(get_response_one.context['trail'].elevation_gain_json[get_response_one.context['trailhead'].name], 500)

    post_response_two = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
      'length': 4.4,
      'elevation_gain': 400,
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

    self.assertRedirects(post_response_two, path)
    get_response_two = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response_two.status_code, 200)
    self.assertTemplateUsed(get_response_two, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response_two.context['reports_list']), 2)
    self.assertEqual(get_response_two.context['trail'].length_json[get_response_two.context['trailhead'].name], '4.9')
    self.assertEqual(get_response_two.context['trail'].elevation_gain_json[get_response_two.context['trailhead'].name], 450)
  
  # update function ignores length from new report if it is an outlier (too high)
  def test_create_report_view_update_trail_increase_length_exceeds(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response_one = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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

    self.assertRedirects(post_response_one, path)
    get_response_one = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    self.assertEqual(get_response_one.context['trail'].length_json[get_response_one.context['trailhead'].name], '5.4')

    post_response_two = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
      'length': 6.5,
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

    self.assertRedirects(post_response_two, path)
    get_response_two = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response_two.status_code, 200)
    self.assertTemplateUsed(get_response_two, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response_two.context['reports_list']), 2)
    self.assertEqual(get_response_two.context['trail'].length_json[get_response_two.context['trailhead'].name], '5.4')
  
  # update function ignores length from new report if it is an outlier (too low)
  def test_create_report_view_update_trail_decrease_length_exceeds(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response_one = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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

    self.assertRedirects(post_response_one, path)
    get_response_one = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    self.assertEqual(get_response_one.context['trail'].length_json[get_response_one.context['trailhead'].name], '5.4')

    post_response_two = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
      'length': 4.3,
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

    self.assertRedirects(post_response_two, path)
    get_response_two = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response_two.status_code, 200)
    self.assertTemplateUsed(get_response_two, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response_two.context['reports_list']), 2)
    self.assertEqual(get_response_two.context['trail'].length_json[get_response_two.context['trailhead'].name], '5.4')

  # update function ignores elevation gain from new report if it is an outlier (too high)
  def test_create_report_view_update_trail_increase_elevation_exceeds(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response_one = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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

    self.assertRedirects(post_response_one, path)
    get_response_one = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    self.assertEqual(get_response_one.context['trail'].elevation_gain_json[get_response_one.context['trailhead'].name], 500)

    post_response_two = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 601,
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

    self.assertRedirects(post_response_two, path)
    get_response_two = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response_two.status_code, 200)
    self.assertTemplateUsed(get_response_two, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response_two.context['reports_list']), 2)
    self.assertEqual(get_response_two.context['trail'].elevation_gain_json[get_response_two.context['trailhead'].name], 500)

  # update function ignores elevation gain from new report if it is an outlier (too low)
  def test_create_report_view_update_trail_decrease_elevation_exceeds(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trail.length_json)
    self.assertIsNone(trail.elevation_gain_json)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response_one = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
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

    self.assertRedirects(post_response_one, path)
    get_response_one = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    self.assertEqual(get_response_one.context['trail'].length_json[get_response_one.context['trailhead'].name], '5.4')
    self.assertEqual(get_response_one.context['trail'].elevation_gain_json[get_response_one.context['trailhead'].name], 500)

    post_response_two = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
      'length': 5.4,
      'elevation_gain': 399,
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

    self.assertRedirects(post_response_two, path)
    get_response_two = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response_two.status_code, 200)
    self.assertTemplateUsed(get_response_two, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response_two.context['reports_list']), 2)
    self.assertEqual(get_response_one.context['trail'].elevation_gain_json[get_response_one.context['trailhead'].name], 500)

  def test_create_report_update_dogs_allowed(self):
    return True

  def test_create_report_update_horses_allowed(self):
    return True


class ReportViewUpdateTrailheadTests(TestCase):
  def test_create_report_update_trailhead_bathroom_status_from_none(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertIsNone(trailhead.bathroom_status)

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
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
      'bathroom_status': 'C',
    })

    self.assertRedirects(post_response, path)
    get_response = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed(get_response, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response.context['reports_list']), 1)
    self.assertEqual(get_response.context['trailhead'].bathroom_status, 'C')
  
  def test_create_report_update_trailhead_bathroom_status_toggle(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters={ 'bathroom_status': 'C' })
    time = datetime.now()
    trail = trailhead.trails.all()[0]

    self.assertEqual(trailhead.bathroom_status, 'C')

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))
    post_response = self.client.post(path, { 
      'region': region.id,
      'trail': trail.id, 
      'trailhead': trailhead.id,
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
      'bathroom_status': 'O'
    })

    self.assertRedirects(post_response, path)
    get_response = self.client.get(path, args=(region.region_slug, trail.trail_slug, trailhead.trailhead_slug,))

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed(get_response, 'trails/reports_trail_trailhead.html')
    self.assertEqual(len(get_response.context['reports_list']), 1)
    self.assertEqual(get_response.context['trailhead'].bathroom_status, 'O')

  def test_create_report_update_bathroom_type(self):
    return True

  def test_create_report_update_access_type(self):
    return True
  
  def test_create_report_update_access_distance(self):
    return True

  def test_create_report_update_pkg_type(self):
    return True

  def test_create_report_update_pkg_capacity(self):
    return True

  def test_create_report_update_access_condition(self):
    return True




class ReportViewErrorTests(TestCase):
  def test_create_report_error_access_distance(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trailhead_trails = trailhead.trails.all()

    path = reverse('reports_trail_trailhead', args=(region.region_slug, trailhead_trails[0].trail_slug, trailhead.trailhead_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trail': trailhead_trails[0].id, 
      'trailhead': trailhead.id,
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
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0.1.')
  
  # test error when begin time is invalid
  def test_create_report_error_time_begin(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Enter a valid time.')
  
  # test error when end time is invalid
  def test_create_report_error_time_end(self):
    region = create_region('CC')
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Enter a valid time.')

  # test parking capacity start error when value is below 0
  def test_create_report_error_parking_capacity_start_low(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')
  
  # test parking capacity start when value is over 100
  def test_create_report_error_parking_capacity_start_high(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
      'pkg_estimate_begin': 120,
      'pkg_estimate_end': 34,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is less than or equal to 100')

  # test parking capacity end error when value is below 0
  def test_create_report_error_parking_capacity_end_low(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test parking capacity end is lower than 100
  def test_create_report_error_parking_capacity_end_low(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
      'pkg_estimate_end': 238,
      'cars_seen': 34,
      'people_seen': 344,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is less than or equal to 100')

  # test cars seen error when value is below 0
  def test_create_report_error_cars_seen(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

  # test people seen error when value is below 0
  def test_create_report_error_people_seen(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
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
    self.assertTemplateUsed(response, 'trails/reports_trail_trailhead.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0')

# <str:region>/<str:trail>/<str:trailhead>/<str:report>/
class SingleReportViewTests(TestCase):
  # renders single report 
  def test_single_report(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    time = datetime.now()
    trailhead_trail = trailhead.trails.all()[0]

    report = create_report(report={
      'region': region,
      'trail': trailhead_trail, 
      'trailhead': trailhead,
    })

    response = self.client.get(reverse('report', args=(region, trailhead_trail.trail_slug, trailhead.trailhead_slug, report.id,)))
    report_post = response.context['report']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/report.html')
    self.assertEqual(report_post.trail.id, report.trail.id)
    self.assertTrue(report_post.trail_begin)
    self.assertTrue(report_post.trail_end)
    self.assertGreaterEqual(report_post.pkg_estimate_begin, 0)
    self.assertLessEqual(report_post.pkg_estimate_begin, 100)
    self.assertGreaterEqual(report_post.pkg_estimate_end, 0)
    self.assertLessEqual(report_post.pkg_estimate_end, 100)
    self.assertTrue(response.context['slugs']['region'])
    self.assertTrue(response.context['slugs']['trail'])
    self.assertTrue(response.context['slugs']['trailhead'])

# reports/<str:day>
# reports/<str:time>
# <trail>/reports/<day>
# <trail>/reports/<time>
class ReportFilterViews(TestCase):
  # returns reports from all trails/regions for a specific day
  def test_filter_by_day(self):
    region = create_region('NC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    create_bulk_reports(region, trailhead.trails.all()[0], trailhead, 3)
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
    trailhead = create_trail_and_trailhead(region=north, filters=None)

    create_report(report={
      'region': north,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'day_hiked': 'S'
    })

    create_report(report={
      'region': north,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'day_hiked': 'Th'
    })

    response = self.client.get(reverse('reports_trail_day', args=(north.region_slug, trailhead.trails.all()[0].trail_slug, 'S',)))

    reports_day = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(len(reports_day), 1)
    self.assertEqual(reports_day[0].day_hiked, 'S')
    self.assertTrue(response.context['advice'])
    self.assertTrue(response.context['caution'])
    self.assertEqual(response.context['reports_total'], 2)

  def test_filter_by_day_trail_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    trailhead_trail = trailhead.trails.all()[0]
    create_report(report={
      'region': region,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'day_hiked': 'Th'
    })

    response = self.client.get(reverse('reports_trail_day', args=(region.region_slug, trailhead_trail.trail_slug, 'S',)))

    trail = response.context['trail']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(trail.name, trailhead_trail.name)
    self.assertEqual(response.context['reports_total'], 1)
    self.assertContains(response, 'No reports found')

  # returns reports from all trails/regions for a time range
  def test_filter_by_time(self):
    north = create_region('NC')
    trailhead = create_trail_and_trailhead(region=north, filters=None)
    period = 'early morning'
    time_begin = time(4, 00)
    time_end = time(6, 59)

    create_report(report={
      'region': north,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'trail_begin': time(4, 1),
      'trail_end': time(7, 30)
    })

    create_report(report={
      'region': north,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'trail_begin': time(3, 00),
      'trail_end': time(6, 00)
    })

    response = self.client.get(reverse('reports_time', args=(period,)))

    reports_time = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_time.html')
    self.assertEqual(len(reports_time), 1)
    self.assertLessEqual(reports_time[0].trail_begin, time_end)
    self.assertGreaterEqual(reports_time[0].trail_begin, time_begin)

  # returns reports from a trail for a specific time
  def test_filter_by_time_trail(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    trailhead_trail = trailhead.trails.all()[0]

    create_report(report={
      'region': region,
      'trail': trailhead_trail, 
      'trailhead': trailhead,
      'trail_begin': time(6, 00),
      'trail_end': time(10, 00)
    })

    create_report(report={
      'region': region,
      'trail': trailhead_trail, 
      'trailhead': trailhead,
      'trail_begin': time(7, 00),
      'trail_end': time(10, 00)
    })

    response = self.client.get(reverse('reports_trail_time', args=(region.region_slug, trailhead_trail.trail_slug, 'early morning',)))

    reports_time = response.context['reports_list']
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(len(reports_time), 1)
    self.assertEqual(reports_time[0].trail, trailhead_trail)
    self.assertGreaterEqual(reports_time[0].trail_begin, time(4, 00))
    self.assertLessEqual(reports_time[0].trail_begin, time(6, 59))
    self.assertTrue(response.context['caution'])
    self.assertTrue(response.context['advice'])

  def test_filter_by_time_trail_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    create_report(report={
      'region': region,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
      'trail_begin': time(13, 00),
      'trail_end': time(16, 00)
    })

    response = self.client.get(reverse('reports_trail_time', args=(region.region_slug, trailhead.trails.all()[0].trail_slug, 'early morning',)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/reports_trail.html')
    self.assertEqual(response.context['trail'].name, trailhead.trails.all()[0].name)
    self.assertEqual(response.context['reports_total'], 1)
    self.assertContains(response, 'No reports found')
  