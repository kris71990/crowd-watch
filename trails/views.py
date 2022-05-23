from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count, Q
from django.forms import ModelChoiceField, CharField
from django.utils import timezone
from django.shortcuts import redirect

import datetime
from decimal import Decimal
from .models import Region, Trail, Trailhead, Report
from .forms import TrailForm, TrailheadForm, ReportForm, SelectDayForm, SelectTimeForm, TrailheadAssociationForm
from .utils import *

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

  trailheads_access_values = trailheads.values('name','access').exclude(access=None)
  trailheads_bathroom_values = trailheads.filter(bathroom_status='O').values('name', 'bathroom_type')

  reports_all_region = Report.objects.filter(trail__region=region).count()
  reports_all_trail = Report.objects.filter(trail=trail).count()

  context = {
    'region': region,
    'trail': trail,
    'trailheads': {
      'obj': trailheads,
      'access': trailheads_access_values,
      'bathroom': trailheads_bathroom_values,
    },
    'summary': {
      'reports_region_count': reports_all_region,
      'reports_trail_count': reports_all_trail
    }
  }
  return render(request, 'trails/trail-summary.html', context)

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
  reports = Report.objects.filter(trailhead=trailhead.id).order_by('-date_hiked')

  if request.method == 'POST':
    form = ReportForm(request.POST)
    if form.is_valid():
      clean = form.cleaned_data
      # if no lengths exist, assign to length given in first report
      if trail.length_json is None:
        trail.length_json = { trailhead.name: str(clean['length']) }
      # if difference between input and existing lengths is close, find average and reassign
      elif abs(Decimal(trail.length_json[trailhead.name]) - clean['length']) < 1:
        existing_length = Decimal(trail.length_json[trailhead.name])
        input_length = clean['length']
        if existing_length > input_length:
          trail.length_json[trailhead.name] = str(Decimal((existing_length + input_length) / 2).quantize(Decimal('1.0')))
        else:
          trail.length_json[trailhead.name] = str(Decimal((input_length + existing_length) / 2).quantize(Decimal('1.0')))
        
      if trail.elevation_gain_json is None:
        trail.elevation_gain_json = { trailhead.name: clean['elevation_gain'] }
      elif abs(trail.elevation_gain_json[trailhead.name] - clean['elevation_gain']) < 100:
        existing_elevation_gain = trail.elevation_gain_json[trailhead.name]
        input_elevation_gain = clean['elevation_gain']
        if existing_elevation_gain > input_elevation_gain:
          trail.elevation_gain_json[trailhead.name] = int((existing_elevation_gain + input_elevation_gain) / 2)
        else:
          trail.elevation_gain_json[trailhead.name] = int((input_elevation_gain + existing_elevation_gain) / 2)
        
      trail.modified = timezone.now(), 
      trailhead.modified = timezone.now()
      trailhead.save(update_fields=['modified'])
      trail.save(update_fields=['modified', 'length_json', 'elevation_gain_json'])
      form.save()
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
  range = parse_time(period)
  reports = Report.objects.filter(trail_begin__gte=range['min']).filter(trail_begin__lte=range['max']).order_by('-date_hiked')
  period_print = '%s (%s - %s)' % (period.capitalize(), range['min'].strftime('%I:%M %p').lstrip('0'), range['max'].strftime('%I:%M %p').lstrip('0'))
  context = { 
    'reports_list': reports,
    'period': period_print,
  }
  return render(request, 'trails/reports_time.html', context)

def reports_trail_time(request, region_slug, trail_slug, period):
  range = parse_time(period)
  region = Region.objects.get(region_slug=region_slug)
  trail = Trail.objects.get(trail_slug=trail_slug)
  reports_total_trail = Report.objects.filter(trail=trail.id)
  reports_filter = Report.objects.filter(trail=trail).filter(trail_begin__gte=range['min']).filter(trail_begin__lte=range['max']).order_by('-date_hiked')
  period_print = '%s (%s-%s)' % (period.capitalize(), range['min'].strftime('%H:%M'), range['max'].strftime('%H:%M'))

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
