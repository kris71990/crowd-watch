from ..models import Trail, Trailhead, Report
from random import randint
from faker import Faker

fake = Faker()

def create_trail(name, region, coordinates):
  return Trail.objects.create(name=name, region=region, coordinates=coordinates)

def create_trailhead(trail, name, coordinates):
  return Trailhead.objects.create(trail=trail, name=name, coordinates=coordinates)

def create_trail_and_trailhead(name, region, coordinates):
  trail = Trail.objects.create(name=name, region=region, coordinates=coordinates)
  return Trailhead.objects.create(trail=trail, name=fake.name(), coordinates=coordinates)

def create_report(report):
  return Report.objects.create(
    trail=report['trail'], trailhead=report['trailhead'], date_hiked=report['date_hiked'], day_hiked=report['day_hiked'], trail_begin=report['trail_begin'], trail_end=report['trail_end'], bathroom_status=report['bathroom_status'], bathroom_type=report['bathroom_type'], access=report['access'], access_condition=report['access_condition'], access_distance=report['access_distance'], car_type=report['car_type'], temperature=report['temperature'], weather_type=report['weather_type'], pkg_location=report['pkg_location'], pkg_estimate_begin=report['pkg_estimate_begin'], pkg_estimate_end=report['pkg_estimate_end'], cars_seen=report['cars_seen'], people_seen=report['people_seen'], horses_seen=report['horses_seen'], dogs_seen=report['dogs_seen']
  )

def create_bulk_reports(region, total):
  trailhead = create_trail_and_trailhead(name=fake.name(), region=region, coordinates=fake.word())
  days = ['M', 'T', 'W', 'Th', 'F', 'S', 'Su']
  br_status = ['C', 'N']
  br_type = ['P', 'FP', 'FR']
  pk = ['UL', 'PL', 'S', 'P']

  for i in range(total):
    create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'access': 'P',
      'date_hiked': fake.date(),
      'day_hiked': days[randint(0, len(days) - 1)],
      'trail_begin': fake.time(),
      'trail_end': fake.time(),
      'bathroom_status': br_status[randint(0, len(br_status) - 1)],
      'bathroom_type': br_type[randint(0, len(br_type) - 1)],
      'pkg_location': pk[randint(0, len(pk) - 1)],
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean()
    })