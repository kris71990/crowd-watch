from django.test import TestCase

from ...models import Region
from ..mocks import create_region

# /regions
class RegionViewTests(TestCase):
  # returns a list of regions
  def test_region_list(self):
    region = create_region('CC')
    response = self.client.get('/trails/regions/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('regions.html')
    self.assertEqual(response.context['regions_table'].all()[0].name, region.name)
    self.assertEqual(response.context['regions_table'].all()[0].reports, 0)
    self.assertEqual(response.context['regions_table'].all()[0].trails, 0)
    self.assertEqual(response.context['regions_table'].all()[0].trailheads, 0)