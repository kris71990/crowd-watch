from ..models import Region, Trail, Trailhead, Report
from random import randint
from faker import Faker
from datetime import time

fake = Faker()

def create_region(name):
  return Region.objects.create(name=name)

def create_trail(region):
  coordinates = fake.word()
  name = fake.name()
  return Trail.objects.create(region=region, name=name, coordinates=coordinates)

def create_trailhead(region, trail, filters):
  coordinates = fake.word()
  name = fake.name()
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

def create_trail_and_trailhead(region, filters):
  trail = create_trail(region)
  return create_trailhead(region, trail, filters)

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
  trail_begin = report['trail_begin'] if 'trail_begin' in report else fake.time()
  trail_end = report['trail_end'] if 'trail_end' in report else fake.time()

  return Report.objects.create(
    region=report['region'],
    trail=report['trail'], 
    trailhead=report['trailhead'], 
    length=fake.pydecimal(positive=True, max_value=10.0, right_digits=2),
    elevation_gain=fake.pyint(min_value=1, max_value=1000),
    day_hiked=day_hiked, 
    trail_begin=trail_begin, 
    trail_end=trail_end,
    access_distance=access_distance, 
    date_hiked=fake.date(), 
    pkg_estimate_begin=fake.pyint(min_value=0, max_value=100), 
    pkg_estimate_end=fake.pyint(min_value=0, max_value=100), 
    cars_seen=fake.pyint(), 
    people_seen=fake.pyint(), 
    horses_seen=fake.boolean(), 
    dogs_seen=fake.boolean(),
    bathroom_status=random_choices['bathroom_status'], 
    bathroom_type=random_choices['bathroom_type'], 
    access=random_choices['access'], 
    access_condition=random_choices['access_condition'], 
    car_type=random_choices['car_type'], 
    temperature=random_choices['temperature'], 
    weather_type=random_choices['weather_type'], 
    pkg_location=random_choices['pkg_location'], 
  )

def create_bulk_reports(region, trail, trailhead, total):
  for i in range(total):
    create_report(report={
      'region': region,
      'trail': trail, 
      'trailhead': trailhead,
    })
  
  return { 'trail': trail, 'trailhead': trailhead }