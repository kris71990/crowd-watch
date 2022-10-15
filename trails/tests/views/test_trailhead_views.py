from django.test import TestCase
from django.urls import reverse

from ...models import Trail, Trailhead
from ..mocks import create_region, create_trail, create_trail_and_trailhead, create_trailhead

# /<region>/<trail>
class TrailheadViewTests(TestCase):
  # returns empty list if no trailheads
  def test_trailhead_list_empty(self):
    region = create_region('CC')
    trail = create_trail(region=region)
    response = self.client.get(reverse('trailheads', args=(region.region_slug, trail.trail_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trailheads.html')
    self.assertContains(response, 'No trailheads found')
    self.assertEqual(response.context['trail'], trail)
    self.assertEqual(response.context['region'], region)
    self.assertQuerysetEqual(response.context['trailheads_list'], [])
    self.assertTrue(response.context['formTh'])
    self.assertTrue(response.context['formDayFilter'])
    self.assertTrue(response.context['formTimeFilter'])

  # returns all trailheads for trail, ordered by most recently modified
  def test_trailhead_list(self):
    region = create_region('CC')
    trail = create_trail(region=region)
    for i in range(2):
      create_trailhead(region=region, trail=trail, filters=None)

    response = self.client.get(reverse('trailheads', args=(region.region_slug, trail.trail_slug,)))
    trailheads = response.context['trailheads_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trailheads.html')
    self.assertContains(response, 'Trailhead')
    self.assertEqual(response.context['trail'], trail)
    self.assertEqual(response.context['region'], region)
    self.assertEqual(len(trailheads), 2)
    self.assertGreater(trailheads[0].modified, trailheads[1].modified)
    self.assertTrue(response.context['formTh'])
    self.assertTrue(response.context['formDayFilter'])
    self.assertTrue(response.context['formTimeFilter'])

  # create trailhead, return new list of trailheads for trail, in order
  def test_create_trailhead_view(self):
    region = create_region('CC')
    trail = create_trail(region=region)
    for i in range(2):
      create_trailhead(region=region, trail=trail, filters=None)

    path = reverse('trailheads', args=(region.region_slug, trail.trail_slug,))
    post_response = self.client.post(path, { 
      'region': region.id, 
      'trails': trail.id, 
      'name': 'abcd xyz', 
      'coordinates': 'sffsd' 
    })
    self.assertRedirects(post_response, path)

    get_response = self.client.get(path, args=(region.region_slug, trail.trail_slug,))
    context = get_response.context

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed(get_response, 'trails/trailheads.html')
    self.assertContains(get_response, 'Trailhead')
    self.assertEqual(context['region'], region)
    self.assertEqual(context['trail'], trail)
    self.assertEqual(len(context['trailheads_list']), 3)
    self.assertGreater(context['trailheads_list'][0].modified, context['trailheads_list'][1].modified)
    self.assertEqual(context['trailheads_list'][0].name, 'abcd xyz')
    self.assertEqual(context['trailheads_list'][0].trailhead_slug, 'abcd-xyz')
    self.assertEqual(context['region'], region)
    self.assertTrue(context['formTh'])
    self.assertTrue(context['formDayFilter'])
    self.assertTrue(context['formTimeFilter'])

# <region>/bathroom
# <region>/access
class TrailheadFilterTests(TestCase):
  # returns trailheads in region with open bathroom
  def test_filter_trailheads_open_bathroom(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters={ 'bathroom_status': 'O' }) # set bathroom to open
    trailhead_closed = create_trailhead(region=region, trail=trailhead.trails.all()[0], filters={ 'bathroom_status': 'C' })
    response = self.client.get(reverse('trailheads_filter_bathroom', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trailheads_filter.html')
    self.assertEqual(response.context['type'], 'bathroom')
    self.assertEqual(len(response.context['trailheads_list']), 1)
    self.assertEqual(response.context['trailheads_list'][0].report__count, 0)
    self.assertEqual(response.context['region'], region)
    self.assertEqual(response.context['trailheads_list'][0].name, trailhead.name)
    self.assertEqual(response.context['trailheads_list'][0].bathroom_status, 'O')

  # returns empty set if no trailheads in region have open bathrooms
  def test_filter_trailheads_open_bathroom_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters={ 'bathroom_status': 'C' }) # set bathroom to closed
    response = self.client.get(reverse('trailheads_filter_bathroom', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trailheads_filter.html')
    self.assertEqual(response.context['type'], 'bathroom')
    self.assertQuerysetEqual(response.context['trailheads_list'], [])
    self.assertEqual(response.context['region'], region)
    self.assertContains(response, 'No trailheads found')

  # returns trailheads in region with paved road access
  def test_filter_trailheads_paved_access(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region, filters={ 'access': 'P' }) # set access to paved
    trailhead_unpaved = create_trailhead(region=region, trail=trailhead.trails.all()[0], filters={ 'access': 'FS' })
    response = self.client.get(reverse('trailheads_filter_access', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trailheads_filter.html')
    self.assertEqual(response.context['type'], 'access')
    self.assertEqual(len(response.context['trailheads_list']), 1)
    self.assertEqual(response.context['trailheads_list'][0].report__count, 0)
    self.assertEqual(response.context['region'], region)
    self.assertEqual(response.context['trailheads_list'][0].name, trailhead.name)
    self.assertEqual(response.context['trailheads_list'][0].access, 'P')

  # return empty set if no trailheads in region have paved access
  def test_filter_trailheads_paved_access_empty(self):
    region = create_region('CC')
    trailhead = create_trail_and_trailhead(region=region,  filters={ 'access': 'FS' }) # set access to service road
    response = self.client.get(reverse('trailheads_filter_access', args=(region.region_slug,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'trails/trailheads_filter.html')
    self.assertEqual(response.context['type'], 'access')
    self.assertQuerysetEqual(response.context['trailheads_list'], [])
    self.assertEqual(response.context['region'], region)
    self.assertContains(response, 'No trailheads found')