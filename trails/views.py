from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count, Q
from django.forms import ModelChoiceField
from django.utils import timezone
from django.shortcuts import redirect

import datetime
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

def trails(request, region):
  trails_list = Trail.objects.annotate(Count('report')).filter(region=region).order_by('-modified')
  
  if request.method == 'POST':
    form = TrailForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(request.path_info)
  else:
    form = TrailForm(initial={ 'region': region }, label_suffix='')
    TrailForm.base_fields['region'].disabled = True

  context = { 
    'trails_list': trails_list,
    'date': timezone.localdate(),
    'region': region,
    'form': form
  }
  return render(request, 'trails/trails.html', context)

def trailheads(request, region, trail):
  trailheads_list = Trailhead.objects.filter(trails__id=trail).annotate(report_count=Count('report', filter=Q(report__trail=trail))).order_by('-modified')
  trail_obj = Trail.objects.filter(pk=trail)

  if request.method == 'POST':
    formTh = TrailheadForm(request.POST)
    if formTh.is_valid():
      trail_obj.update(modified=timezone.now())
      formTh.save()
      return HttpResponseRedirect(request.path_info)
  else:
    TrailheadForm.base_fields['trail'] = ModelChoiceField(queryset=trail_obj)
    formTh = TrailheadForm(initial={ 'trail': trail }, label_suffix='')

  formDayFilter = SelectDayForm()
  formTimeFilter = SelectTimeForm()
  context = {
    'date': timezone.localdate(),
    'trailheads_list': trailheads_list,
    'region': region,
    'trail': trail_obj[0],
    'formTh': formTh,
    'formDayFilter': formDayFilter,
    'formTimeFilter': formTimeFilter,
  }
  return render(request, 'trails/trailheads.html', context)

def trail_summary(request, region, trail):
  trail_obj = Trail.objects.get(pk=trail)
  trailheads_obj = Trailhead.objects.filter(trails=trail)

  trailheads_access_values = trailheads_obj.values('name','access').exclude(access=None)
  trailheads_bathroom_values = trailheads_obj.filter(bathroom_status='O').values('name', 'bathroom_type')

  reports_all_region = Report.objects.filter(trail__region=region).count()
  reports_all_trail = Report.objects.filter(trail=trail).count()

  context = {
    'region': region,
    'trail': trail_obj,
    'trailheads': {
      'obj': trailheads_obj,
      'access': trailheads_access_values,
      'bathroom': trailheads_bathroom_values,
    },
    'summary': {
      'reports_region_count': reports_all_region,
      'reports_trail_count': reports_all_trail
    }
  }
  return render(request, 'trails/trail-summary.html', context)

def trailheads_filter_bathroom(request, region):
  trailheads_list = Trailhead.objects.filter(region=region).filter(bathroom_status='O').annotate(Count('report')).order_by('-modified')
  context = {
    'date': timezone.localdate(),
    'trailheads_list': trailheads_list,
    'region': region,
    'type': 'bathroom',
  }
  return render(request, 'trails/trailheads_filter.html', context)

def trailheads_filter_access(request, region):
  trailheads_list = Trailhead.objects.filter(region=region).filter(access='P').annotate(Count('report')).order_by('-modified')
  context = {
    'date': timezone.localdate(),
    'trailheads_list': trailheads_list,
    'region': region,
    'type': 'access',
  }
  return render(request, 'trails/trailheads_filter.html', context)

def reports_trailhead(request, region, trailhead):
  reports = Report.objects.filter(trailhead=trailhead).order_by('-date_hiked')
  trailhead_obj = Trailhead.objects.get(pk=trailhead)

  context = {
    'date': timezone.localdate(),
    'reports_list': reports,
    'region': region,
    'trailhead': trailhead_obj,
  }
  return render(request, 'trails/reports_trailhead.html', context)

def reports_trail_trailhead(request, region, trail, trailhead):
  reports = Report.objects.filter(trailhead=trailhead).order_by('-date_hiked')
  trailhead_obj = Trailhead.objects.filter(pk=trailhead)
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
    ReportForm.base_fields['trail'] = ModelChoiceField(queryset=trail_obj)
    ReportForm.base_fields['trailhead'] = ModelChoiceField(queryset=trailhead_obj)
    ReportForm.base_fields['trail'].disabled = True
    ReportForm.base_fields['trailhead'].disabled = True
    form = ReportForm(initial={ 'trail': trail, 'trailhead': trailhead }, label_suffix='')

  context = {
    'date': timezone.localdate(),
    'reports_list': reports,
    'region': region, 
    'trail_obj': trail_obj[0],
    'trailhead': trailhead_obj[0],
    'form': form
  }
  print(context)
  return render(request, 'trails/reports_trail_trailhead.html', context)

def reports_trail(request, region, trail):
  reports = Report.objects.filter(trail=trail).order_by('-modified')
  trail_obj = Trail.objects.get(pk=trail)

  context = {
    'date': timezone.localdate(),
    'reports_list': reports,
    'region': region,
    'trail': trail_obj,
  }
  return render(request, 'trails/reports_trail.html', context)

def report(request, region, trail, trailhead, report):
  report = Report.objects.get(pk=report)
  context = {
    'report': report,
  }
  return render(request, 'trails/report.html', context)

def reports_filter(request, region, trail):
  if request.method == 'POST':
    filter = request.POST.get('days_field')
    if filter is None:
      form = SelectTimeForm(request.POST)
      if form.is_valid():
        time = form.cleaned_data['time_field']
        return redirect('reports_trail_time', region=region, trail=trail, period=time)
    else:
      form = SelectDayForm(request.POST)
      if form.is_valid():
        day = form.cleaned_data['days_field']
        return redirect('reports_trail_day', region=region, trail=trail, day=day)

def reports_day(request, day):
  formatted_day = abbreviate_day(day)
  reports = Report.objects.filter(day_hiked=formatted_day).order_by('-date_hiked')
  context = { 
    'reports_list': reports, 
    'day': day.capitalize(),
    'date': timezone.localdate(),
  }
  return render(request, 'trails/reports_day.html', context)

def reports_trail_day(request, region, trail, day):
  formatted_day = abbreviate_day(day)
  print(formatted_day)
  reports_total_trail = Report.objects.filter(trail=trail)
  reports_filter = reports_total_trail.filter(day_hiked=formatted_day).order_by('-date_hiked')
  trail_obj = Trail.objects.get(pk=trail)
  
  if not reports_filter:
    total = len(reports_total_trail)
    context = {
      'region': region,
      'trail': trail_obj,
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
      'trail': trail_obj,
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

def reports_trail_time(request, region, trail, period):
  range = parse_time(period)
  reports_total_trail = Report.objects.filter(trail=trail)
  reports_filter = Report.objects.filter(trail=trail).filter(trail_begin__gte=range['min']).filter(trail_begin__lte=range['max']).order_by('-date_hiked')
  period_print = '%s (%s-%s)' % (period.capitalize(), range['min'].strftime('%H:%M'), range['max'].strftime('%H:%M'))
  trail_obj = Trail.objects.get(pk=trail)

  if not reports_filter:
    total = len(reports_total_trail)
    context = {
      'date': timezone.localdate(),
      'region': region,
      'trail': trail_obj,
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
      'trail': trail_obj,
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
