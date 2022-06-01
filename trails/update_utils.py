from decimal import Decimal
from django.utils import timezone

# Updates to Trail (elevation_gain, length, dogs_allowed, horses_allowed)
# Updates to Trailhead (bathroom_status, access_condition, pkg_capacity)

# called on report submission
# if report has a length, length is updated with length if none exists
# or algorithmically adjusts length based on consensus of previous reported values
def update_trail_length(length, trail, trailhead_name):
  if length is not None:
    if (trail.length_json is None or trail.length_json[trailhead_name] is None or 
        trail.length_json[trailhead_name] == 'None'):
      trail.length_json = { trailhead_name: str(length) }
    # if difference between input and existing lengths is close, find average and reassign
    elif abs(Decimal(trail.length_json[trailhead_name]) - length) <= 1:
      existing_length = Decimal(trail.length_json[trailhead_name])
      input_length = length
      if existing_length > input_length:
        trail.length_json[trailhead_name] = str(Decimal((existing_length + input_length) / 2).quantize(Decimal('1.0')))
      else:
        trail.length_json[trailhead_name] = str(Decimal((input_length + existing_length) / 2).quantize(Decimal('1.0')))
    
    trail.modified = timezone.now(), 
    trail.save(update_fields=['modified', 'length_json'])
  
# called on report submission
# if report has an elevation gain, elevation gain is updated with data if none exists
# or algorithmically adjusts elevation based on consensus of previous reported values
def update_trail_elevation(elevation, trail, trailhead_name):      
  if (elevation is not None):  
    if (trail.elevation_gain_json is None or trail.elevation_gain_json[trailhead_name] is None or 
        trail.length_json[trailhead_name] == 'None'):
      trail.elevation_gain_json = { trailhead_name: elevation }
    elif abs(trail.elevation_gain_json[trailhead_name] - elevation) <= 100:
      existing_elevation_gain = trail.elevation_gain_json[trailhead_name]
      input_elevation_gain = elevation
      if existing_elevation_gain > input_elevation_gain:
        trail.elevation_gain_json[trailhead_name] = int((existing_elevation_gain + input_elevation_gain) / 2)
      else:
        trail.elevation_gain_json[trailhead_name] = int((input_elevation_gain + existing_elevation_gain) / 2)
    
    trail.modified = timezone.now(), 
    trail.save(update_fields=['modified', 'elevation_gain_json'])

# called on every report submission; updates trail with dog and horse sightings array
def update_trail_dogs_allowed(dogs, trail):
  if trail.dogs_allowed == []:
    if dogs:
      trail.dogs_allowed.append(1)
      trail.dogs_allowed.append(0)
    else: 
      trail.dogs_allowed.append(0)
      trail.dogs_allowed.append(1)
  else:
    if dogs:
      trail.dogs_allowed[0] += 1
    else: 
      trail.dogs_allowed[1] += 1

  trail.modified = timezone.now()
  trail.save(update_fields=['modified', 'dogs_allowed'])

def update_trail_horses_allowed(horses, trail):
  if trail.horses_allowed == []:
    if horses:
      trail.horses_allowed.append(1)
      trail.horses_allowed.append(0)
    else: 
      trail.horses_allowed.append(0)
      trail.horses_allowed.append(1)
  else:
    if horses:
      trail.horses_allowed[0] += 1
    else: 
      trail.horses_allowed[1] += 1

  trail.modified = timezone.now()
  trail.save(update_fields=['modified', 'horses_allowed'])
    
# called on report submission if user submits relevant data
# always update bathroom status and access condition of trailhead to newest information available
def update_trailhead_bathroom_status(bathroom_status, trailhead):
  trailhead.bathroom_status = bathroom_status
  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'bathroom_status'])

def update_trailhead_access_condition(access_condition, trailhead):
  trailhead.access_condition = access_condition
  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'access_condition'])

# called on every report submission, maintains parking capacity attribute on trailhead model based on
# reported car/parking data
def update_trailhead_parking_capacity(cars, max, trailhead):
  capacity = cars * (100 / max)
  if trailhead.pkg_capacity is None:
    trailhead.pkg_capacity = capacity
  elif abs(trailhead.pkg_capacity - capacity) <= 5:
    trailhead.pkg_capacity = (trailhead.pkg_capacity + capacity) / 2

  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'pkg_capacity'])


# called when new data is submitted on attributes that should not change often
# structural elements of a trailhead
def update_trailhead_bathroom_type(bathroom_type, trailhead):
  trailhead.bathroom_type = bathroom_type
  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'bathroom_type'])

def update_trailhead_access(access, trailhead):
  trailhead.access = access
  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'access'])

def update_trailhead_access_distance(access_distance, trailhead):
  trailhead.access_distance = access_distance
  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'access_distance'])

def update_trailhead_parking_type(parking_type, trailhead):
  trailhead.pkg_type = parking_type
  trailhead.modified = timezone.now()
  trailhead.save(update_fields=['modified', 'pkg_type'])