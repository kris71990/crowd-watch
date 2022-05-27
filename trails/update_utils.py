from decimal import Decimal
from django.utils import timezone

# called on report submission
# if report has a length, clean_form['trail'] is updated with length if none exists
# or algorithmically adjusts length based on consensus of previous reported values
def update_trail_length(clean_form):
  if clean_form['length'] is not None:
    if (clean_form['trail'].length_json is None or clean_form['trail'].length_json[clean_form['trailhead'].name] is None or 
        clean_form['trail'].length_json[clean_form['trailhead'].name] == 'None'):
      clean_form['trail'].length_json = { clean_form['trailhead'].name: str(clean_form['length']) }
    # if difference between input and existing lengths is close, find average and reassign
    elif abs(Decimal(clean_form['trail'].length_json[clean_form['trailhead'].name]) - clean_form['length']) <= 1:
      existing_length = Decimal(clean_form['trail'].length_json[clean_form['trailhead'].name])
      input_length = clean_form['length']
      if existing_length > input_length:
        clean_form['trail'].length_json[clean_form['trailhead'].name] = str(Decimal((existing_length + input_length) / 2).quantize(Decimal('1.0')))
      else:
        clean_form['trail'].length_json[clean_form['trailhead'].name] = str(Decimal((input_length + existing_length) / 2).quantize(Decimal('1.0')))
    
    clean_form['trail'].modified = timezone.now(), 
    clean_form['trail'].save(update_fields=['modified', 'length_json', 'elevation_gain_json'])
  
# called on report submission
# if report has an elevation gain, clean_form['elevation_gain'] is updated with data if none exists
# or algorithmically adjusts elevation based on consensus of previous reported values
def update_trail_elevation(clean_form):      
  if (clean_form['elevation_gain'] is not None):  
    if (clean_form['trail'].elevation_gain_json is None or clean_form['trail'].elevation_gain_json[clean_form['trailhead'].name] is None or 
        clean_form['trail'].length_json[clean_form['trailhead'].name] == 'None'):
      clean_form['trail'].elevation_gain_json = { clean_form['trailhead'].name: clean_form['elevation_gain'] }
    elif abs(clean_form['trail'].elevation_gain_json[clean_form['trailhead'].name] - clean_form['elevation_gain']) <= 100:
      existing_elevation_gain = clean_form['trail'].elevation_gain_json[clean_form['trailhead'].name]
      input_elevation_gain = clean_form['elevation_gain']
      if existing_elevation_gain > input_elevation_gain:
        clean_form['trail'].elevation_gain_json[clean_form['trailhead'].name] = int((existing_elevation_gain + input_elevation_gain) / 2)
      else:
        clean_form['trail'].elevation_gain_json[clean_form['trailhead'].name] = int((input_elevation_gain + existing_elevation_gain) / 2)
    
    clean_form['trail'].modified = timezone.now(), 
    clean_form['trail'].save(update_fields=['modified', 'length_json', 'elevation_gain_json'])

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
