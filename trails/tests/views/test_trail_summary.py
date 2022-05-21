from django.test import TestCase
from django.urls import reverse
from faker import Faker

from ...models import Trail
from ..mocks import create_region, create_trail_and_trailhead

fake = Faker()

# /<region>/<trail>/summary
class TrailSummaryViewTests(TestCase):
  # returns summary of trail data
  def test_trail_summary_no_reports(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name=fake.name(), filters=None)
    trailhead_trails = trailhead.trails.all()

    response = self.client.get(reverse('trail_summary', args=(region.region_slug, trailhead_trails[0].trail_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trail_summary.html')
    self.assertContains(response, 'Summary')
    self.assertEqual(response.context['trail'], trailhead_trails[0])
    self.assertEqual(response.context['region'], region)
    self.assertQuerysetEqual(response.context['trailheads']['obj'][0].name, trailhead.name)
    self.assertEqual(response.context['summary']['reports_region_count'], 0)
    self.assertEqual(response.context['summary']['reports_region_count'], 0)