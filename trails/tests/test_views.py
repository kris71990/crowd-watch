from django.test import TestCase
from django.urls import reverse

from ..models import Trail

class RegionViewTests(TestCase):
  def test_region_list(self):
    response = self.client.get(reverse('regions'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.context['regions_list']), 9)
    self.assertIsInstance(response.context['regions_list'][0], tuple)