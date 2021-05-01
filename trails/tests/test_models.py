from django.test import TestCase

from ..models import Trail

class TrailModelTests(TestCase):
  # create trail with all required fields returns a trail
  def test_create_trail(self):
    trail = Trail(name='test_name', region='CC', coordinates='-23.44, -11.44')
    self.assertIs(trail.name, 'test_name')
    self.assertIs(trail.region, 'CC')
    self.assertIs(trail.coordinates, '-23.44, -11.44')
