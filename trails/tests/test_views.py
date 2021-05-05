from django.test import TestCase
from django.urls import reverse

from ..models import Trail, Trailhead, Report

class RegionViewTests(TestCase):
  # /regions - returns a list of regions
  def test_region_list(self):
    response = self.client.get(reverse('regions'))
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.context['regions_list']), 9)
    self.assertIsInstance(response.context['regions_list'][0], tuple)

class TrailViewTests(TestCase):
  # /list
  # returns empty list when no trails exist
  def test_trail_list_empty(self):
    response = self.client.get(reverse('trail_list'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'No trails found')
    self.assertQuerysetEqual(response.context['trails_list'], [])

  # /trail_list - all trails when some exist
  # /trail_list - all trails when some exist from multiple regions
  # /trail_list - all trails ordered correctly

  # /<region> - returns all trails in region
  # /<region> - create a trail, return new list of trails


# class TrailheadViewTests(TestCase)
  # /<region>/<trail> - returns all trailheads for trail 

# class ReportViewTests(TestCase):
  # /<region>/<trail>/<reports> - returns all reports for trail
  # /<region>/<trail>/<trailhead> - returns all reports for trailhead