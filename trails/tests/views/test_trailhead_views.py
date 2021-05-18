from django.test import TestCase
from django.urls import reverse
from faker import Faker

from ...models import Trail, Trailhead
from ..mocks import create_trail, create_trailhead

fake = Faker()

# /<region>/<trail>
class TrailheadViewTests(TestCase):
  # returns empty list if no trailheads
  def test_trailhead_list_empty(self):
    region = 'CC'
    trail = create_trail(name=fake.name(), region=region, coordinates=fake.word())
    response = self.client.get(reverse('trailheads', args=(region, trail.id,)))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(response, 'No trailheads found')
    self.assertEqual(response.context['trail'], trail)
    self.assertQuerysetEqual(response.context['trailheads_list'], [])

  # returns all trailheads for trail, ordered by most recently modified
  def test_trailhead_list(self):
    region = 'CC'
    trail = create_trail(name=fake.name(), region=region, coordinates=fake.word())
    for i in range(2):
      create_trailhead(trail=trail, name=fake.name(), coordinates=fake.word())

    response = self.client.get(reverse('trailheads', args=(region, trail.id,)))
    trailheads = response.context['trailheads_list']

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(response, 'Trailhead')
    self.assertEqual(response.context['trail'], trail)
    self.assertEqual(len(trailheads), 2)
    self.assertGreater(trailheads[0].modified, trailheads[1].modified)


  # create trailhead, return new list of trailheads for trail, in order
  def test_create_trailhead_view(self):
    region = 'CC'
    trail_name = 'test_trail'
    trail = create_trail(name=trail_name, region=region, coordinates=fake.word())
    for i in range(2):
      create_trailhead(trail=trail, name=fake.name(), coordinates=fake.word())

    path = reverse('trailheads', args=(region, trail.id,))
    post_response = self.client.post(path, { 'trail': trail.id, 'name': 'abcd', 'coordinates': 'sffsd' })
    self.assertRedirects(post_response, path)

    get_response = self.client.get(path, args=(region, trail.id,))
    trailheads = get_response.context['trailheads_list']

    self.assertEqual(get_response.status_code, 200)
    self.assertTemplateUsed('trailheads.html')
    self.assertContains(get_response, 'Trailhead')
    self.assertEqual(len(trailheads), 3)
    self.assertGreater(trailheads[0].modified, trailheads[1].modified)
    self.assertEqual(trailheads[0].name, 'abcd')