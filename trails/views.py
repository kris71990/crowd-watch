from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Trail, Trailhead
from .forms import TrailForm

def regions(request):
  regions_list = Trail.REGION_CHOICES
  context = { 'regions_list': regions_list }
  return render(request, 'trails/regions.html', context)

def trails(request, region):
  trails_list = Trail.objects.filter(region=region)
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

def add_trail(request, region):
  print(request.POST)
  # try:
  #   trail_to_add = request.POST['name']
  # except (KeyError, Trail.DoesNotExist):
  #   trails_list = Trail.objects.filter(region=region)
  #   return render(request, 'trails/trails.html', { 
  #     'trails_list': trails_list,
  #     'region': region,
  #   })
  # else:
  #   trail_instance = get_object_or_404(Trail, region=region, name=request.POST['name'])
  #   Trail()


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
