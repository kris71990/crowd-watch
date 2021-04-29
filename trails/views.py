from django.http import HttpResponse
from django.shortcuts import render

from .models import Trail, Trailhead

def regions(request):
  regions_list = Trail.REGION_CHOICES
  context = { 'regions_list': regions_list }
  return render(request, 'trails/regions.html', context)

def trails(request, region):
  trails_list = Trail.objects.filter(region=region)
  context = { 
    'trails_list': trails_list,
    'region': region,
  }
  return render(request, 'trails/trails.html', context)

def trailheads(request, region, trail):
  trailheads_list = Trailhead.objects.filter(trail=trail)
  context = {
    'trailheads_list': trailheads_list,
    'region': region,
    'trail': trail
  }
  return render(request, 'trails/trailheads.html', context)

def reports_trailhead(request, region, trail, trailhead):
  return HttpResponse('Reports for %s trailhead - %s (%s)' % (trailhead, trail, region))

def reports_trail(request, region, trail):
  return HttpResponse('Reports for %s (%s)' % (trail, region))

def index(request):
  return HttpResponse('Hello World: Trails index.')
