from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import Trail, Trailhead
from .forms import TrailForm, TrailheadForm

def regions(request):
  regions_list = Trail.REGION_CHOICES
  context = { 'regions_list': regions_list }
  return render(request, 'trails/regions.html', context)

def trail_list(request):
  trails_list = Trail.objects.all().order_by('-modified')
  context = { 'trails_list': trails_list }
  return render(request, 'trails/trail_list.html', context)

def trails(request, region):
  trails_list = Trail.objects.filter(region=region).order_by('-modified')
  
  if request.method == 'POST':
    form = TrailForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    form = TrailForm()

  context = { 
    'trails_list': trails_list,
    'region': region,
    'form': form
  }
  return render(request, 'trails/trails.html', context)

def trailheads(request, region, trail):
  trailheads_list = Trailhead.objects.filter(trail=trail).order_by('-modified')
  trail_obj = Trail.objects.get(pk=trail)

  if request.method == 'POST':
    form = TrailheadForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    form = TrailheadForm()

  context = {
    'trailheads_list': trailheads_list,
    'region': region,
    'trail': trail_obj,
    'form': form
  }
  return render(request, 'trails/trailheads.html', context)

def reports_trailhead(request, region, trail, trailhead):
  return HttpResponse('Reports for %s trailhead - %s (%s)' % (trailhead, trail, region))

def reports_trail(request, region, trail):
  return HttpResponse('Reports for %s (%s)' % (trail, region))

def index(request):
  return HttpResponse('Hello World: Trails index.')
