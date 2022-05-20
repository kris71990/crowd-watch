from ..models import Region, Trail, Trailhead, Report
from random import randint
from faker import Faker

fake = Faker()

def create_region(name):
  return Region.objects.create(name=name)

def create_trail(region, name):
  coordinates = fake.word()
  return Trail.objects.create(name=name, region=region, coordinates=coordinates)

def create_trailhead(region, trail, name, filters):
  coordinates = fake.word()
  if filters is None:
    trailhead = Trailhead.objects.create(region=region, name=name, coordinates=coordinates)
    trailhead.trails.add(trail)
    return trailhead
  elif 'br' in filters:
    trailhead = Trailhead.objects.create(region=region, name=name, coordinates=coordinates, bathroom_status=filters['br'])
    trailhead.trails.add(trail)
    return trailhead
  elif 'access' in filters:
    trailhead = Trailhead.objects.create(region=region, name=name, coordinates=coordinates, access=filters['access'])
    trailhead.trails.add(trail)
    return trailhead

def create_trail_and_trailhead(region, name, filters):
  coordinates = fake.word()
  trail = create_trail(name, region)
  return create_trailhead(trail, region, fake.name(), filters)

def generate_random_choices():
  day_hiked = Report.DAYS[randint(0, len(Report.DAYS) - 1)][0]
  car_type = Report.CAR_TYPES[randint(0, len(Report.CAR_TYPES) - 1)][0]
  weather_type = Report.WEATHER_TYPE[randint(0, len(Report.WEATHER_TYPE) - 1)][0]
  temperature = Report.TEMPERATURES[randint(0, len(Report.TEMPERATURES) - 1)][0]
  bathroom_status = Report.BATHROOM_STATUS[randint(0, len(Report.BATHROOM_STATUS) - 1)][0]
  bathroom_type = Report.BATHROOM_TYPE[randint(0, len(Report.BATHROOM_TYPE) - 1)][0]
  access = Report.ACCESS_TYPES[randint(0, len(Report.ACCESS_TYPES) - 1)][0]
  access_condition = Report.ACCESS_CONDITIONS[randint(0, len(Report.ACCESS_CONDITIONS) - 1)][0]
  pkg_location = Report.PARKING_TYPES[randint(0, len(Report.PARKING_TYPES) - 1)][0]
  return {
    'access': access, 'day_hiked': day_hiked, 'car_type': car_type, 'weather_type': weather_type, 'temperature': temperature, 
    'bathroom_status': bathroom_status, 'bathroom_type': bathroom_type, 'access_condition': access_condition, 'pkg_location': pkg_location
  }

def create_report(report):
  random_choices = generate_random_choices()
  if 'access_distance' in report:
    access_distance = report['access_distance']
  else:
    access_distance = 0.1

  day_hiked = report['day_hiked'] if 'day_hiked' in report else random_choices['day_hiked']

  return Report.objects.create(
    region=report['region'],
    trail=report['trail'], 
    trailhead=report['trailhead'], 
    date_hiked=report['date_hiked'], 
    trail_begin=report['trail_begin'], 
    trail_end=report['trail_end'], 
    access_distance=access_distance, 
    pkg_estimate_begin=report['pkg_estimate_begin'], 
    pkg_estimate_end=report['pkg_estimate_end'], 
    cars_seen=report['cars_seen'], 
    people_seen=report['people_seen'], 
    horses_seen=report['horses_seen'], 
    dogs_seen=report['dogs_seen'],
    day_hiked=day_hiked, 
    bathroom_status=random_choices['bathroom_status'], 
    bathroom_type=random_choices['bathroom_type'], 
    access=random_choices['access'], 
    access_condition=random_choices['access_condition'], 
    car_type=random_choices['car_type'], 
    temperature=random_choices['temperature'], 
    weather_type=random_choices['weather_type'], 
    pkg_location=random_choices['pkg_location'], 
  )

def create_bulk_reports(region, total):
  trailhead = create_trail_and_trailhead(name=fake.name(), region=region, filters=None)

  for i in range(total):
    random_choices = generate_random_choices()
    create_report(report={
      'trail': trailhead.trail, 
      'trailhead': trailhead,
      'date_hiked': fake.date(),
      'trail_begin': fake.time(),
      'trail_end': fake.time(),
      'pkg_estimate_begin': fake.pyint(min_value=0, max_value=100),
      'pkg_estimate_end': fake.pyint(min_value=0, max_value=100),
      'cars_seen': fake.pyint(),
      'people_seen': fake.pyint(),
      'horses_seen': fake.boolean(),
      'dogs_seen': fake.boolean(),
      'access_distance': randint(0, 20),
      'access': random_choices['access'],
      'access_condition': random_choices['access_condition'],
      'day_hiked': random_choices['day_hiked'],
      'bathroom_status': random_choices['bathroom_status'],
      'bathroom_type': random_choices['bathroom_type'],
      'pkg_location': random_choices['pkg_location'],
      'car_type': random_choices['car_type'],
      'temperature': random_choices['temperature'],
      'weather_type': random_choices['weather_type']
    })