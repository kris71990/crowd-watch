from datetime import time

def parse_time(period):
  if period == 'early morning':
    min = time(4, 00)
    max = time(6, 59)
  elif period == 'mid morning':
    min = time(7, 00)
    max = time(9, 59)
  elif period == 'late morning':
    min = time(10, 00)
    max = time(11, 59)
  elif period == 'afternoon':
    min = time(12, 00)
    max = time(16, 59)
  elif period == 'evening':
    min = time(17, 00)
    max = time(21, 59)
  else:
    min = time(22, 00)
    max = time(3, 59)
  return { 'min': min, 'max': max }

def create_advice(type, filtered, total):
  if total < 1:
    return None

  ratio = (filtered / total) * 100
  if (ratio > 80):
    caution = 'red'
    if type == 'time':
      advice = 'Crowded: at least 4 of 5 people hike around this time - try going earlier or later to avoid crowds.'
    else:
      advice = 'Crowded: at least 4 of 5 people hike on this day - choose a different day to avoid crowds.'
  elif (ratio > 50):
    caution = 'orange'
    if type == 'time':
      advice = 'Popular: a majority of hikers hike around this time - consider going earlier or later to avoid crowds.'
    else:
      advice = 'Popular: a majority of hikers hike on this day - consider choosing a different day to avoid crowds.'
  elif (ratio > 40):
    caution = 'orange'
    if type == 'time':
      advice = 'Expect people: roughly half of hikers hike at this time - consider going earlier or later to avoid people.'
    else:
      advice = 'Expect people: roughly half of hikers choose this day - consider choosing a different day to avoid people.'
  elif (ratio > 25):
    caution = 'yellow'
    if type == 'time':
      advice = 'A few people: roughly 3 in 10 hikers hike at this time - this is a good time to avoid people'
    else:
      advice = 'A few people: roughly 3 of every 10 hikers hike on this day - this is a good day to avoid people.'
  elif(ratio > 10):
    caution = 'green'
    if type == 'time':
      advice = 'Minimal traffic: about 2 in 10 people hike at this time - this is a good time to avoid people.'
    else:
      advice = 'Minimal traffic: about 2 in 10 people hike on this day - this is a good day to avoid crowds.'
  else:
    caution = 'green'
    if type == 'time':
      advice = 'Solitude: few people hike at this time - this is an ideal time to avoid people.'
    else:
      advice = 'Solitude: few people hike on this day - this an ideal day to avoid people.'
  return { 'advice': advice, 'caution': caution }

def find_tuple_display_value(model_tuple, value):
  target = [item for item in model_tuple if item[0] == value]
  return target[0][1]

def abbreviate_day(day):
  if day == 'thursday' or day == 'sunday':
    return day[:2].capitalize()
  else:
    return day[0].upper()
