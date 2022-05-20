from django import template

register = template.Library()

def lookup(d, key):
  return d[key]

def get_item(dictionary, key): 
  if dictionary and dictionary.get(key):
    return dictionary.get(key)

register.filter('lookup', lookup)
register.filter('get_item', get_item)