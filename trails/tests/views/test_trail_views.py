from django.test import TestCase
from django.urls import reverse

from ...models import Trail
from ..mocks import create_trail, create_region

# /list
class TrailListViewTests(TestCase):
  # returns empty list when no trails exist
  def test_trail_list_empty(self):
    response = self.client.get(reverse('trail_list'))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trail_list.html')
    self.assertContains(response, 'No trails found')
    self.assertQuerysetEqual(response.context['trails_list'], [])
    self.assertTrue(response.context['date'])

  # returns all trails when some exist, regardless of region, ordered by most recent
  def test_trail_list(self):
    regions = ['CC', 'WW', 'NC']
    for i in range(3):
      region = create_region(i)
      create_trail(region=region)
      
    response = self.client.get(reverse('trail_list'))
    trails = response.context['trails_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trail_list.html')
    self.assertContains(response, 'Trail Feed')
    self.assertEqual(len(trails), 3)
    self.assertGreater(trails[0].modified, trails[1].modified)
    self.assertGreater(trails[1].modified, trails[2].modified)

# /<region>
class TrailListByRegionViewTests(TestCase):
  # returns empty list when no trails exist in region
  def test_trail_list_by_region_empty(self):
    region = create_region('CC')
    response = self.client.get(reverse('trails', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trails.html')
    self.assertContains(response, 'No trails found')
    self.assertQuerysetEqual(response.context['trails_list'], [])
    self.assertEqual(response.context['region'].name, region.name)
    self.assertTrue(response.context['form'])
    self.assertTrue(response.context['date'])

  # returns all trails when some exist in region, ordered by most recent
  def test_trail_list_by_region(self):
    region = create_region('CC')
    for i in range(3):
      create_trail(region=region)

    response = self.client.get(reverse('trails', args=(region.region_slug,)))
    trails = response.context['trails_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trails.html')
    self.assertContains(response, 'Central Cascades Trails')
    self.assertEqual(len(trails), 3)
    self.assertGreater(trails[0].modified, trails[1].modified)
    self.assertGreater(trails[1].modified, trails[2].modified)
    self.assertEqual(response.context['region'].name, region.name)
    self.assertEqual(trails[0].report__count, 0)
    self.assertTrue(response.context['form'])
    self.assertTrue(response.context['date'])

  # create a trail, return new list of trails for region, in order
  def test_create_trail(self):
    region = create_region('CC')
    for i in range(3):
      create_trail(region=region)

    path = reverse('trails', args=(region.region_slug,))
    post_response = self.client.post(path, { 'name': 'dssf xyz', 'region': region.id, 'coordinates': 'sffsd' })
    self.assertRedirects(post_response, path)

    get_response = self.client.get(path, args=(region.region_slug,))
    trails = get_response.context['trails_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed(get_response, 'trails/trails.html')
    self.assertContains(get_response, 'Central Cascades Trails')
    self.assertEqual(len(trails), 4)
    self.assertGreater(trails[0].modified, trails[1].modified)
    self.assertEqual(trails[0].name, 'dssf xyz')
    self.assertEqual(trails[0].trail_slug, 'dssf-xyz')
    self.assertIsNone(trails[0].elevation_gain_json)
    self.assertIsNone(trails[0].length_json)
    self.assertTrue(response.context['form'])
    self.assertEqual(response.context['region'].name, region.name)
    self.assertEqual(trails[0].report__count, 0)
