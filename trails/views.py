from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count
from django.forms import ModelChoiceField
from django.utils import timezone
from django.shortcuts import redirect

from .models import Trail, Trailhead, Report
from .forms import TrailForm, TrailheadForm, ReportForm, SelectDayForm, SelectTimeForm
from .utils import *

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
    'trailheads_list': trailheads_list,
    'region': region,
    'trail': trail_obj[0],
    'formTh': formTh,
    'formDayFilter': formDayFilter,
    'formTimeFilter': formTimeFilter,
  }
  return render(request, 'trails/trailheads.html', context)

def trailheads_filter_bathroom(request, region):
  trailheads_list = Trailhead.objects.filter(trail__region=region).filter(bathroom_status='O').annotate(Count('report')).order_by('-modified')
  context = {
    'trailheads_list': trailheads_list,
    'region': region,
    'type': 'bathroom',
  }
  return render(request, 'trails/trailheads_filter.html', context)

def trailheads_filter_access(request, region):
  trailheads_list = Trailhead.objects.filter(trail__region=region).filter(access='P').annotate(Count('report')).order_by('-modified')
  context = {
    'trailheads_list': trailheads_list,
    'region': region,
    'type': 'access',
  }
  return render(request, 'trails/trailheads_filter.html', context)

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
  reports = Report.objects.filter(day_hiked=day).order_by('-day_hiked')
  context = { 'reports_list': reports, 'day': day }
  return render(request, 'trails/reports_day.html', context)

def reports_trail_day(request, region, trail, day):
  reports_total_trail = Report.objects.filter(trail=trail)
  reports_filter = reports_total_trail.filter(day_hiked=day).order_by('-day_hiked')
  
  if not reports_filter:
    trail_obj = Trail.objects.get(pk=trail)
    total = len(reports_total_trail)
    context = {
      'region': region,
      'trail_day_empty': trail_obj,
      'day': day,
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
      'day': day,
      'advice': advice['advice'],
      'caution': advice['caution']
    }
  return render(request, 'trails/reports.html', context)

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
  reports_total_trail = Report.objects.filter(trail=trail)
  reports_filter = Report.objects.filter(trail=trail).filter(trail_begin__gte=range['min']).filter(trail_begin__lte=range['max'])
  period_print = '%s (%s-%s)' % (period.capitalize(), range['min'], range['max'])

  if not reports_filter:
    trail_obj = Trail.objects.get(pk=trail)
    total = len(reports_total_trail)
    context = {
      'region': region,
      'trail_time_empty': trail_obj,
      'period': period_print,
      'reports_total': total,
    }
  else:
    total_trail_report_count = len(reports_total_trail)
    filter_report_count = len(reports_filter)
    advice = create_advice('time', filter_report_count, total_trail_report_count)
    context = { 
      'reports_list': reports_filter,
      'reports_total': total_trail_report_count,
      'reports_list_total': filter_report_count,
      'period': period_print,
      'advice': advice['advice'],
      'caution': advice['caution']
    }
    
  return render(request, 'trails/reports.html', context)

def index(request):
  return render(request, 'trails/index.html')
