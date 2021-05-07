from django.test import TestCase

# /regions
class RegionViewTests(TestCase):
  # returns a list of regions
  def test_region_list(self):
    response = self.client.get('/trails/regions/')
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('regions.html')
    self.assertEqual(len(response.context['regions_list']), 9)
    self.assertIsInstance(response.context['regions_list'][0], tuple)