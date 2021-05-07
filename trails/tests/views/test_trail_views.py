from django.test import TestCase
from django.urls import reverse
from faker import Faker

from ...models import Trail
from ..mocks import create_trail

fake = Faker()

# /list
class TrailListViewTests(TestCase):
  # returns empty list when no trails exist
  def test_trail_list_empty(self):
    response = self.client.get(reverse('trail_list'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trail_list.html')

    self.assertContains(response, 'No trails found')
    self.assertQuerysetEqual(response.context['trails_list'], [])

  # returns all trails when some exist, regardless of region, ordered by most recent
  def test_trail_list(self):
    regions = ['CC', 'WW', 'NC']
    for i in range(3):
      create_trail(name=fake.name(), region=regions[i], coordinates=fake.word())
      
    response = self.client.get(reverse('trail_list'))
    trails = response.context['trails_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trail_list.html')
    self.assertContains(response, 'Trail Feed')

    self.assertEqual(len(trails), 3)
    self.assertGreater(trails[0].modified, trails[1].modified)
    self.assertGreater(trails[1].modified, trails[2].modified)

# /<region>
class TrailListByRegionViewTests(TestCase):
  # returns empty list when no trails exist in region
  def test_trail_list_by_region_empty(self):
    region = 'CC'
    response = self.client.get(reverse('trails', args=(region,)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trails.html')

    self.assertContains(response, 'No trails found')
    self.assertQuerysetEqual(response.context['trails_list'], [])
    self.assertEqual(response.context['region'], region)
    self.assertIsNotNone(response.context['form'])

  # returns all trails when some exist in region, ordered by most recent
  def test_trail_list_by_region(self):
    region = 'CC'
    for i in range(3):
      create_trail(name=fake.name(), region=region, coordinates=fake.word())

    response = self.client.get(reverse('trails', args=(region,)))
    trails = response.context['trails_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trails.html')
    self.assertContains(response, 'Central Cascades Trails')

    self.assertEqual(len(trails), 3)
    self.assertGreater(trails[0].modified, trails[1].modified)
    self.assertGreater(trails[1].modified, trails[2].modified)
    self.assertEqual(response.context['region'], region)
    self.assertIsNotNone(response.context['form'])

  # create a trail, return new list of trails for region, in order
  def test_create_trail(self):
    region = 'CC'
    for i in range(3):
      create_trail(name=fake.name(), region=region, coordinates=fake.word())

    path = reverse('trails', args=(region,))
    post_response = self.client.post(path, { 'name': 'dssf', 'region': region, 'coordinates': 'sffsd' })
    self.assertRedirects(post_response, path)

    get_response = self.client.get(path, args=(region,))
    trails = get_response.context['trails_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed('trails.html')
    self.assertContains(get_response, 'Central Cascades Trails')
    self.assertEqual(len(trails), 4)
    self.assertGreater(trails[0].modified, trails[1].modified)
    self.assertEqual(trails[0].name, 'dssf')
