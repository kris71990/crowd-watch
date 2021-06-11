from django.test import TestCase
from django.urls import reverse
from faker import Faker

from ...models import Trail
from ..mocks import create_trail, create_trail_and_trailhead

fake = Faker()

# /<region>/<trail>/summary
class TrailSummaryViewTests(TestCase):
  # returns summary of trail data
  def test_trail_summary(self):
    region = 'CC'
    trailheads = create_trail_and_trailhead(name=fake.name(), region=region, coordinates=fake.word(), filters=None)

    response = self.client.get(reverse('trail_summary', args=(region, trailheads.trail.id,)))

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('trail_summary.html')
    self.assertContains(response, 'Summary')
    self.assertEqual(response.context['trail'], trailheads.trail)
    self.assertEqual(response.context['region'], region)
    self.assertQuerysetEqual(response.context['trailheads'][0].name, trailheads.name)