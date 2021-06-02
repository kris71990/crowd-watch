from datetime import time

def parse_time(period):
  if period == 'morning':
    min = time(0, 00)
    max = time(11, 59)
  elif period == 'afternoon':
    min = time(12, 00)
    max = time(17, 59)
  elif period == 'evening':
    min = time(18, 00)
    max = time(21, 59)
  else:
    min = time(22, 00)
    max = time(23, 59)
  return { 'min': min, 'max': max }

def create_advice(total, filter):
  ratio = (filter / total) * 100
  if (ratio > 80):
    advice = 'Crowded: at least 4 of 5 people hike on this day - choose a different day to avoid crowds.'
  elif (ratio > 50):
    advice = 'Popular: a majority of hikers hike on this day - consider choosing a different day to avoid crowds.'
  elif (ratio > 40):
    advice = 'Expect people: roughly half of hikers choose this day - consider choosing a different day to avoid people.'
  elif (ratio > 25):
    advice = 'Expect people: roughly 3 of every 10 hikers hike on this day - this is a good day to avoid crowds.'
  elif(ratio > 10):
    advice = 'Minimal traffic: about 2 in 10 people hike on this day - this is a good day to avoid crowds'
  else:
    advice = 'Solitude: few people hike on this day - this is the ideal day to avoid people'
  return advice
