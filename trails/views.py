from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count, Q
from django.forms import ModelChoiceField, CharField
from django.utils import timezone
from django.shortcuts import redirect

import datetime
from .models import Region, Trail, Trailhead, Report
from .forms import TrailForm, TrailheadForm, ReportForm, SelectDayForm, SelectTimeForm, TrailheadAssociationForm
from .utils import *
from .update_utils import *

def regions(request):
  trail_count = Count('trail', distinct=True)
  report_count = Count('report', distinct=True)
  trailhead_count = Count('trailhead', distinct=True)
  
  regions_list = Region.objects.annotate(trails=trail_count, trailheads=trailhead_count, reports=report_count).order_by('-trails')

  context = { 
    'regions_table': regions_list,
  }
  return render(request, 'trails/regions.html', context)

def trail_list(request):
  trails_list = Trail.objects.annotate(Count('report')).order_by('-modified')
  context = { 
    'date': timezone.localdate(),
    'trails_list': trails_list
  }
  return render(request, 'trails/trail_list.html', context)

def reports_list(request):
  reports_list = Report.objects.all().order_by('-date_hiked')
  context = { 
    'reports_list': reports_list, 
    'date': timezone.localdate(),
  }
  return render(request, 'trails/report_list.html', context)

def trails(request, region_slug):
  region = Region.objects.get(region_slug=region_slug)
  trails_list = Trail.objects.annotate(Count('report')).filter(region=region.id).order_by('-modified')
  
  if request.method == 'POST':
    form = TrailForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    form = TrailForm(initial={ 'region': region }, label_suffix='')

  context = { 
    'trails_list': trails_list,
    'date': timezone.localdate(),
    'region': region,
    'form': form
  }
  return render(request, 'trails/trails.html', context)

def trailheads(request, region_slug, trail_slug):
  region = Region.objects.get(region_slug=region_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  trailheads_list = Trailhead.objects.filter(trails__id=trail.id).annotate(report_count=Count('report', filter=Q(report__trail=trail.id))).order_by('-modified')

  if request.method == 'POST':
    formTh = TrailheadForm(request.POST)
    if formTh.is_valid():
      trail.modified = timezone.now()
      trail.save(update_fields=['modified'])
      formTh.save()
      return HttpResponseRedirect(request.path_info)
  else:
    formTh = TrailheadForm(initial={ 'trails': trail, 'region': region }, label_suffix='')

  formDayFilter = SelectDayForm()
  formTimeFilter = SelectTimeForm()
  context = {
    'date': timezone.localdate(),
    'trailheads_list': trailheads_list,
    'region': region,
    'trail': trail,
    'formTh': formTh,
    'formDayFilter': formDayFilter,
    'formTimeFilter': formTimeFilter,
  }
  return render(request, 'trails/trailheads.html', context)

def trail_summary(request, region_slug, trail_slug):
  region = Region.objects.get(region_slug=region_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  trailheads = Trailhead.objects.filter(trails=trail.id)

  reports_all_region = Report.objects.filter(trail__region=region).count()
  reports_all_trail = Report.objects.filter(trail=trail).count()
  advice = create_advice('trail', reports_all_trail, reports_all_region)

  context = {
    'region': region,
    'trail': trail,
    'trailheads': trailheads,
    'summary': {
      'reports_region_count': reports_all_region,
      'reports_trail_count': reports_all_trail,
      'advice': advice
    }
  }
  return render(request, 'trails/trail_summary.html', context)

def trailheads_filter_bathroom(request, region_slug):
  region = Region.objects.get(region_slug=region_slug)
  trailheads_list = Trailhead.objects.filter(region=region.id).filter(bathroom_status='O').annotate(Count('report')).order_by('-modified')
  context = {
    'date': timezone.localdate(),
    'trailheads_list': trailheads_list,
    'region': region,
    'type': 'bathroom',
  }
  return render(request, 'trails/trailheads_filter.html', context)

def trailheads_filter_access(request, region_slug):
  region = Region.objects.get(region_slug=region_slug)
  trailheads_list = Trailhead.objects.filter(region=region.id).filter(access='P').annotate(Count('report')).order_by('-modified')
  context = {
    'date': timezone.localdate(),
    'trailheads_list': trailheads_list,
    'region': region,
    'type': 'access',
  }
  return render(request, 'trails/trailheads_filter.html', context)

def reports_trailhead(request, region_slug, trailhead_slug):
  region = Region.objects.get(region_slug=region_slug)
  trailhead = Trailhead.objects.get(trailhead_slug=trailhead_slug)
  reports = Report.objects.filter(trailhead=trailhead.id).order_by('-date_hiked')

  context = {
    'date': timezone.localdate(),
    'reports_list': reports,
    'region': region,
    'trailhead': trailhead,
  }
  return render(request, 'trails/reports_trailhead.html', context)

def reports_trail_trailhead(request, region_slug, trail_slug, trailhead_slug):
  region = Region.objects.get(region_slug=region_slug)
  trailhead = Trailhead.objects.get(trailhead_slug=trailhead_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  reports = Report.objects.filter(trail=trail.id, trailhead=trailhead.id).order_by('-date_hiked')

  if request.method == 'POST':
    form = ReportForm(request.POST)
    if form.is_valid():
      clean = form.cleaned_data
      form.save()
      if clean['length']: update_trail_length(clean['length'], trail, trailhead.name)
      if clean['elevation_gain']: update_trail_elevation(clean['elevation_gain'], trail, trailhead.name)
      update_trail_dogs_allowed(clean['dogs_seen'], trail)
      update_trail_horses_allowed(clean['horses_seen'], trail)

      if clean['bathroom_status']: update_trailhead_bathroom_status(clean['bathroom_status'], trailhead)
      if clean['bathroom_type']: update_trailhead_bathroom_type(clean['bathroom_type'], trailhead)
      if clean['access']: update_trailhead_access(clean['access'], trailhead)
      if clean['access_condition']: update_trailhead_access_condition(clean['access_condition'], trailhead)
      if clean['access_distance']: update_trailhead_access_distance(clean['access_distance'], trailhead)
      if clean['pkg_location']: update_trailhead_parking_type(clean['pkg_location'], trailhead)

      max_capacity = clean['pkg_estimate_begin'] if clean['pkg_estimate_begin'] > clean['pkg_estimate_end'] else clean['pkg_estimate_end']
      update_trailhead_parking_capacity(clean['cars_seen'], max_capacity, trailhead)
      return HttpResponseRedirect(request.path_info)
  else:
    form = ReportForm(initial={ 'region': region, 'trail': trail, 'trailhead': trailhead }, label_suffix='')

  context = {
    'date': timezone.localdate(),
    'reports_list': reports,
    'region': region, 
    'trail': trail,
    'trailhead': trailhead,
    'form': form
  }
  return render(request, 'trails/reports_trail_trailhead.html', context)

def reports_trail(request, region_slug, trail_slug):
  region = Region.objects.get(region_slug=region_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  reports = Report.objects.filter(trail=trail.id).order_by('-date_hiked')

  context = {
    'date': timezone.localdate(),
    'reports_list': reports,
    'region': region,
    'trail': trail,
  }
  return render(request, 'trails/reports_trail.html', context)

def report(request, region_slug, trail_slug, trailhead_slug, report):
  report = Report.objects.get(pk=report)
  context = {
    'report': report,
    'slugs': { 'region': region_slug, 'trail': trail_slug, 'trailhead': trailhead_slug }
  }
  return render(request, 'trails/report.html', context)

def reports_filter(request, region_slug, trail_slug):
  if request.method == 'POST':
    filtered = request.POST.get('days_field')
    if filtered is None:
      form = SelectTimeForm(request.POST)
      if form.is_valid():
        time = form.cleaned_data['time_field']
        return redirect('reports_trail_time', region_slug=region_slug, trail_slug=trail_slug, period=time)
    else:
      form = SelectDayForm(request.POST)
      if form.is_valid():
        day = form.cleaned_data['days_field']
        return redirect('reports_trail_day', region_slug=region_slug, trail_slug=trail_slug, day=day)

def reports_day(request, day):
  formatted_day = abbreviate_day(day)
  reports = Report.objects.filter(day_hiked=formatted_day).order_by('-date_hiked')
  context = { 
    'reports_list': reports, 
    'day': day.capitalize(),
    'date': timezone.localdate(),
  }
  return render(request, 'trails/reports_day.html', context)

def reports_trail_day(request, region_slug, trail_slug, day):
  formatted_day = abbreviate_day(day)
  region = Region.objects.get(region_slug=region_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  reports_total_trail = Report.objects.filter(trail=trail.id)
  reports_filter = reports_total_trail.filter(day_hiked=formatted_day).order_by('-date_hiked')
  
  if not reports_filter:
    total = len(reports_total_trail)
    context = {
      'region': region,
      'trail': trail,
      'day': day.capitalize(),
      'reports_total': total,
    }
  else:
    total_trail_report_count = len(reports_total_trail)
    filter_report_count = len(reports_filter)
    advice = create_advice('day', filter_report_count, total_trail_report_count)
    context = { 
      'reports_list': reports_filter,
      'reports_total': total_trail_report_count,
      'reports_list_total': filter_report_count,
      'trail': trail,
      'region': region,
      'day': day,
      'date': timezone.localdate(),
      'advice': advice['advice'],
      'caution': advice['caution']
    }
  return render(request, 'trails/reports_trail.html', context)

def reports_time(request, period):
  time_range = parse_time(period)
  reports = Report.objects.filter(trail_begin__gte=time_range['min']).filter(trail_begin__lte=time_range['max']).order_by('-date_hiked')
  period_print = '%s (%s - %s)' % (period.capitalize(), time_range['min'].strftime('%I:%M %p').lstrip('0'), time_range['max'].strftime('%I:%M %p').lstrip('0'))
  context = { 
    'reports_list': reports,
    'period': period_print,
  }
  return render(request, 'trails/reports_time.html', context)

def reports_trail_time(request, region_slug, trail_slug, period):
  time_range = parse_time(period)
  region = Region.objects.get(region_slug=region_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  reports_total_trail = Report.objects.filter(trail=trail.id)
  reports_filter = Report.objects.filter(trail=trail).filter(trail_begin__gte=time_range['min']).filter(trail_begin__lte=time_range['max']).order_by('-date_hiked')
  period_print = '%s (%s-%s)' % (period.capitalize(), time_range['min'].strftime('%H:%M'), time_range['max'].strftime('%H:%M'))

  if not reports_filter:
    total = len(reports_total_trail)
    context = {
      'date': timezone.localdate(),
      'region': region,
      'trail': trail,
      'period': period_print,
      'reports_total': total,
    }
  else:
    total_trail_report_count = len(reports_total_trail)
    filter_report_count = len(reports_filter)
    advice = create_advice('time', filter_report_count, total_trail_report_count)
    context = { 
      'date': timezone.localdate(),
      'region': region,
      'trail': trail,
      'reports_list': reports_filter,
      'reports_total': total_trail_report_count,
      'reports_list_total': filter_report_count,
      'period': period_print,
      'advice': advice['advice'],
      'caution': advice['caution']
    }
    
  return render(request, 'trails/reports_trail.html', context)

def index(request):
  return render(request, 'trails/index.html')
