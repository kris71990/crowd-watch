from django.test import TestCase
from django.urls import reverse
from faker import Faker

from ...models import Trail
from ..mocks import create_region, create_trail_and_trailhead, create_bulk_reports

fake = Faker()

# /<region>/<trail>/summary
class TrailSummaryViewTests(TestCase):
  # returns summary of trail data
  def test_trail_summary_no_reports(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters=None)
    trailhead_trails = trailhead.trails.all()

    response = self.client.get(reverse('trail_summary', args=(region.region_slug, trailhead_trails[0].trail_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trail_summary.html')
    self.assertContains(response, 'Summary')
    self.assertEqual(response.context['trail'], trailhead_trails[0])
    self.assertEqual(response.context['region'], region)
    self.assertQuerysetEqual(response.context['trailheads'][0].name, trailhead.name)
    self.assertEqual(response.context['summary']['reports_region_count'], 0)
    self.assertEqual(response.context['summary']['reports_region_count'], 0)
    self.assertIsNone(response.context['summary']['advice'])

  def test_trail_summary_with_reports(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters={ 'bathroom_status': 'O', 'bathroom_type': 'P', 'access': 'FS' })
    trail = trailhead.trails.all()[0]
    reports = create_bulk_reports(region, trail, trailhead, 10)

    response = self.client.get(reverse('trail_summary', args=(region.region_slug, trail.trail_slug,)))
    summary = response.context['summary']
    trailheads = response.context['trailheads'].all()

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trail_summary.html')
    self.assertContains(response, 'Facilities and Access')
    self.assertContains(response, 'Popularity')
    self.assertIsNotNone(summary['advice'])
    self.assertEqual(summary['reports_region_count'], 10)
    self.assertEqual(summary['reports_trail_count'], 10)

    self.assertEqual(len(trailheads), 1)
    self.assertContains(response, trailheads[0].name)
    self.assertEqual(trailheads[0], reports['trailhead'])
    self.assertEqual(trailheads[0].access, 'FS')
    self.assertEqual(trailheads[0].bathroom_type, 'P')
    self.assertEqual(trailheads[0].bathroom_status, 'O')
