from django.test import TestCase
from django.urls import reverse
from faker import Faker

from ...models import Trail, Trailhead
from ..mocks import create_region, create_trail, create_trail_and_trailhead, create_trailhead

fake = Faker()

# /<region>/<trail>
class TrailheadViewTests(TestCase):
  # returns empty list if no trailheads
  def test_trailhead_list_empty(self):
    region = create_region('CC')
    trail = create_trail(region=region, name=fake.name())
    response = self.client.get(reverse('trailheads', args=(region.region_slug, trail.trail_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(response, 'No trailheads found')
    self.assertEqual(response.context['trail'], trail)
    self.assertEqual(response.context['region'], region)
    self.assertQuerysetEqual(response.context['trailheads_list'], [])

  # returns all trailheads for trail, ordered by most recently modified
  def test_trailhead_list(self):
    region = create_region('CC')
    trail = create_trail(region=region, name=fake.name())
    for i in range(2):
      create_trailhead(region=region, trail=trail, name=fake.name(), filters=None)

    response = self.client.get(reverse('trailheads', args=(region.region_slug, trail.trail_slug,)))
    trailheads = response.context['trailheads_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(response, 'Trailhead')
    self.assertEqual(response.context['trail'], trail)
    self.assertEqual(len(trailheads), 2)
    self.assertGreater(trailheads[0].modified, trailheads[1].modified)

  # create trailhead, return new list of trailheads for trail, in order
  def test_create_trailhead_view(self):
    region = create_region('CC')
    trail_name = 'test_trail'
    trail = create_trail(region=region, name=trail_name)
    for i in range(2):
      create_trailhead(region=region, trail=trail, name=fake.name(), filters=None)

    path = reverse('trailheads', args=(region.region_slug, trail.trail_slug,))
    post_response = self.client.post(path, { 
      'region': region.id, 
      'trails': trail.id, 
      'name': 'abcd', 
      'coordinates': 'sffsd' 
    })
    self.assertRedirects(post_response, path)

    get_response = self.client.get(path, args=(region.region_slug, trail.trail_slug,))
    trailheads = get_response.context['trailheads_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(get_response, 'Trailhead')
    self.assertEqual(len(trailheads), 3)
    self.assertGreater(trailheads[0].modified, trailheads[1].modified)
    self.assertEqual(trailheads[0].name, 'abcd')

  def test_create_trailhead_error_access_distance(self):
    region = create_region('CC')
    trail_name = 'test_trail'
    trailhead = create_trail_and_trailhead(region=region, name=trail_name, filters=None)
    trailhead_trails = trailhead.trails.all()

    path = reverse('trailheads', args=(region.region_slug, trailhead_trails[0].trail_slug,))
    response = self.client.post(path, { 
      'region': region.id,
      'trails': trailhead_trails[0].id, 
      'name': 'abcd', 
      'coordinates': 'sffsd',
      'access_distance': 0,
    })

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(response, 'Ensure this value is greater than or equal to 0.1.')


# <region>/bathroom
# <region>/access
class TrailheadFilterTests(TestCase):
  # returns trailheads in region with open bathroom
  def test_filter_trailheads_open_bathroom(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name='test', filters={ 'br': 'O' }) # set bathroom to open
    response = self.client.get(reverse('trailheads_filter_bathroom', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads_filter.html')
    self.assertEqual(response.context['type'], 'bathroom')
    self.assertEqual(len(response.context['trailheads_list']), 1)
    self.assertEqual(response.context['trailheads_list'][0].name, trailhead.name)

  # returns empty set if no trailheads in region have open bathrooms
  def test_filter_trailheads_open_bathroom_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name='test', filters={ 'br': 'C' }) # set bathroom to closed
    response = self.client.get(reverse('trailheads_filter_bathroom', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads_filter.html')
    self.assertEqual(response.context['type'], 'bathroom')
    self.assertQuerysetEqual(response.context['trailheads_list'], [])
    self.assertContains(response, 'No trailheads found')

  # returns trailheads in region with paved road access
  def test_filter_trailheads_paved_access(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name='test', filters={ 'access': 'P' }) # set access to paved
    response = self.client.get(reverse('trailheads_filter_access', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads_filter.html')
    self.assertEqual(response.context['type'], 'access')
    self.assertEqual(len(response.context['trailheads_list']), 1)
    self.assertEqual(response.context['trailheads_list'][0].name, trailhead.name)

  # return empty set if no trailheads in region have paved access
  def test_filter_trailheads_paved_access_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, name='test', filters={ 'access': 'FS' }) # set access to service road
    response = self.client.get(reverse('trailheads_filter_access', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads_filter.html')
    self.assertEqual(response.context['type'], 'access')
    self.assertQuerysetEqual(response.context['trailheads_list'], [])
    self.assertContains(response, 'No trailheads found')