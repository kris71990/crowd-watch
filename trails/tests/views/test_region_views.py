from django.test import TestCase

from ...models import Region
from ..mocks import create_region, create_trail_and_trailhead, create_report

class IndexViewTests(TestCase):
  def test_index_view(self):
    response = self.client.get('/trails/')
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Welcome to the trail crowd tracker')
    self.assertTemplateUsed(response, 'trails/index.html')

# /regions
class RegionViewTests(TestCase):
  # returns a list of regions
  def test_region_list(self):
    region = create_region('CC')
    response = self.client.get('/trails/regions/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/regions.html')
    self.assertEqual(response.context['regions_table'].all()[0].name, region.name)
    self.assertEqual(response.context['regions_table'].all()[0].reports, 0)
    self.assertEqual(response.context['regions_table'].all()[0].trails, 0)
    self.assertEqual(response.context['regions_table'].all()[0].trailheads, 0)

  def test_region_list_multiple_regions_with_data(self):
    region_one = create_region('NC')
    region_two = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region_two, filters=None)
    create_report(report={
      'region': region_two,
      'trail': trailhead.trails.all()[0], 
      'trailhead': trailhead,
    })

    response = self.client.get('/trails/regions/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/regions.html')
    self.assertEqual(response.context['regions_table'].all()[0].name, region_two.name)
    self.assertEqual(response.context['regions_table'].all()[0].reports, 1)
    self.assertEqual(response.context['regions_table'].all()[0].trails, 1)
    self.assertEqual(response.context['regions_table'].all()[0].trailheads, 1)
    self.assertEqual(response.context['regions_table'].all()[1].name, region_one.name)
    self.assertEqual(response.context['regions_table'].all()[1].reports, 0)
    self.assertEqual(response.context['regions_table'].all()[1].trails, 0)
    self.assertEqual(response.context['regions_table'].all()[1].trailheads, 0)