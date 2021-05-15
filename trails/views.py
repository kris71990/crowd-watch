from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count
from django.forms import ModelChoiceField

from .models import Trail, Trailhead, Report
from .forms import TrailForm, TrailheadForm, ReportForm

def regions(request):
  regions_list = Trail.REGION_CHOICES
  context = { 'regions_list': regions_list }
  return render(request, 'trails/regions.html', context)

def trail_list(request):
  trails_list = Trail.objects.annotate(Count('report')).order_by('-modified')
  context = { 'trails_list': trails_list }
  return render(request, 'trails/trail_list.html', context)

def trails(request, region):
  trails_list = Trail.objects.filter(region=region).annotate(Count('report')).order_by('-modified')
  
  if request.method == 'POST':
    form = TrailForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    form = TrailForm(initial={ 'region': region })

  context = { 
    'trails_list': trails_list,
    'region': region,
    'form': form
  }
  return render(request, 'trails/trails.html', context)

def trailheads(request, region, trail):
  trailheads_list = Trailhead.objects.filter(trail=trail).annotate(Count('report')).order_by('-modified')
  trail_obj = Trail.objects.filter(pk=trail)

  if request.method == 'POST':
    form = TrailheadForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    TrailheadForm.base_fields['trail'] = ModelChoiceField(queryset=trail_obj)
    form = TrailheadForm(initial={ 'trail': trail })

  context = {
    'trailheads_list': trailheads_list,
    'region': region,
    'trail': trail_obj[0],
    'form': form
  }
  return render(request, 'trails/trailheads.html', context)

def reports_trailhead(request, region, trail, trailhead):
  reports = Report.objects.filter(trailhead=trailhead).order_by('-modified')
  trailhead_obj = Trailhead.objects.get(pk=trailhead)
  trail_obj = Trail.objects.filter(pk=trail)

  if request.method == 'POST':
    form = ReportForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    trailhead_choices = Trailhead.objects.filter(trail=trail)
    ReportForm.base_fields['trail'] = ModelChoiceField(queryset=trail_obj)
    ReportForm.base_fields['trailhead'] = ModelChoiceField(queryset=trailhead_choices)
    form = ReportForm(initial={ 'trail': trail, 'trailhead': trailhead })

  context = {
    'reports_list': reports,
    'region': region, 
    'trailhead': trailhead_obj,
    'form': form
  }
  return render(request, 'trails/reports.html', context)

def reports_trail(request, region, trail):
  reports = Report.objects.filter(trail=trail).order_by('-modified')
  trail_obj = Trail.objects.get(pk=trail)

  context = {
    'reports_list': reports,
    'region': region,
    'trail': trail_obj,
  }
  return render(request, 'trails/reports.html', context)

def report(request, region, trail, trailhead, report):
  report = Report.objects.get(pk=report)
  context = {
    'report': report,
  }
  return render(request, 'trails/report.html', context)

def index(request):
  return render(request, 'trails/index.html')
