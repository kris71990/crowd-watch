from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count
from django.forms import ModelChoiceField
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, time

from .models import Trail, Trailhead, Report
from .forms import TrailForm, TrailheadForm, ReportForm

def regions(request):
  regions_list = Trail.REGION_CHOICES
  region_trail_count = []
  for i in Trail.REGION_CHOICES:
    trail_count = len(Trail.objects.filter(region=i[0]).values('name'))
    region_trail_count.append(trail_count)

  context = { 
    'regions_list': regions_list,
    'region_trail_count': region_trail_count
  }
  return render(request, 'trails/regions.html', context)

def trail_list(request):
  trails_list = Trail.objects.annotate(Count('report')).order_by('-modified')
  context = { 'trails_list': trails_list }
  return render(request, 'trails/trail_list.html', context)

def reports_list(request):
  reports_list = Report.objects.all().order_by('-modified')
  context = { 'reports_list': reports_list }
  return render(request, 'trails/report_list.html', context)

def trails(request, region):
  trails_list = Trail.objects.annotate(Count('report')).filter(region=region).order_by('-modified')
  
  if request.method == 'POST':
    form = TrailForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    form = TrailForm(initial={ 'region': region }, label_suffix='')

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
      trail_obj.update(modified=timezone.now())
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    TrailheadForm.base_fields['trail'] = ModelChoiceField(queryset=trail_obj)
    form = TrailheadForm(initial={ 'trail': trail }, label_suffix='')

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
      trail_obj.update(modified=timezone.now())
      trailhead_obj.modified = timezone.now()
      trailhead_obj.save(update_fields=['modified'])
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    trailhead_choices = Trailhead.objects.filter(trail=trail)
    ReportForm.base_fields['trail'] = ModelChoiceField(queryset=trail_obj)
    ReportForm.base_fields['trailhead'] = ModelChoiceField(queryset=trailhead_choices)
    form = ReportForm(initial={ 'trail': trail, 'trailhead': trailhead }, label_suffix='')

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

def reports_day(request, day):
  reports = Report.objects.filter(day_hiked=day).order_by('-day_hiked')
  context = { 'reports_list': reports }
  return render(request, 'trails/reports_day.html', context)

def reports_filter(request, region, trail):
  print(region, trail)
  if request.method == 'POST':
    day = request.POST.get('day')
    print(day)
    return HttpResponseRedirect(reverse('reports_trail_day'), args=(request, region, trail, day,))

def reports_trail_day(request, region, trail, day):
  reports = Report.objects.filter(trail=trail).filter(day_hiked=day).order_by('-day_hiked')
  context = { 'reports_list_trail': reports }
  return render(request, 'trails/reports.html', context)

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

def reports_time(request, period):
  range = parse_time(period)
  reports = Report.objects.filter(trail_begin__gte=range['min']).filter(trail_begin__lte=range['max'])
  period_print = '%s (%s-%s)' % (period.capitalize(), range['min'], range['max'])
  context = { 
    'reports_list': reports,
    'period': period_print,
  }
  return render(request, 'trails/reports_time.html', context)

def reports_trail_time(request, region, trail, period):
  range = parse_time(period)
  reports = Report.objects.filter(trail=trail).filter(trail_begin__gte=range['min']).filter(trail_begin__lte=range['max'])
  period_print = '%s (%s-%s)' % (period.capitalize(), range['min'], range['max'])
  context = { 
    'reports_list_trail': reports,
    'period': period_print,
  }
  return render(request, 'trails/reports_time.html', context)

def index(request):
  return render(request, 'trails/index.html')
