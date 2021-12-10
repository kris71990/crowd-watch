from django.contrib import admin
from django.db.models import Count
from .models import Region, Trail, Trailhead, Report

class RegionAdmin(admin.ModelAdmin):
  def get_queryset(self, request):
    trail_count = Count('trail', distinct=True)
    report_count = Count('report', distinct=True)
    trailhead_count = Count('trailhead', distinct=True)
    return Region.objects.annotate(trails_count=trail_count, trailheads_count=trailhead_count, reports_count=report_count)

  def get_trails(self, obj):
    return obj.trails_count

  def get_trailheads(self, obj):
    return obj.trailheads_count

  def get_reports(self, obj):
    return obj.reports_count

  get_trails.short_description = 'Trails'
  get_trailheads.short_description = 'Trailheads'
  get_reports.short_description = 'Reports'

  readonly_fields = ['id']
  list_display = ('name', 'get_trails', 'get_trailheads', 'get_reports')

class TrailAdmin(admin.ModelAdmin):
  def get_queryset(self, request):
    return Trail.objects.annotate(report_count=Count('report'))

  def get_reports(self, obj):
    return obj.report_count

  def get_trailheads(self, obj):
    trailheads = []
    for trailhead in obj.trailheads.all():
      trailheads.append(trailhead.name)
    return trailheads

  get_trailheads.short_description = 'Trailheads'
  get_reports.short_description = 'Reports'

  readonly_fields = ['id', 'modified', 'get_trailheads']
  fieldsets = (
    (None, {
      'fields': ('name', 'region', 'coordinates', 'length', 'elevation_gain')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )
  list_display = ('name', 'region', 'get_trailheads', 'get_reports')
  list_filter = ['region']

class TrailheadAdmin(admin.ModelAdmin):
  def get_trails(self, obj):
    trails = []
    for trail in obj.trails.all():
      trails.append(trail.name)
    return trails
  get_trails.short_description = 'Trails'

  readonly_fields = ['id', 'modified', 'get_trails']
  fieldsets = (
    ('For', {
      'fields': ['region', 'trails']
    }),
    ('Trailhead Data', {
      'fields': ('name', 'coordinates', 'access', 'access_distance', 'pkg_type', 'pkg_capacity', 'bathroom_type', 'bathroom_status')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )
  list_display = ('name', 'get_trails')
  list_filter = ['region']

class ReportAdmin(admin.ModelAdmin):
  readonly_fields = ('id', 'modified')

  def get_trail(self, obj):
    return obj.trail.name

  def get_trailhead(self, obj):
    return obj.trailhead.name

  get_trail.short_description = 'Trail'
  get_trailhead.short_description = 'Trailhead'

  fieldsets = (
    ('For Trail', {
      'fields': ('region', 'trail', 'trailhead')
    }),
    (None, {
      'fields': ('date_hiked', 'day_hiked', 'car_type', 'access', 'access_distance', 'access_condition', 'trail_begin', 'trail_end', 'weather_type', 'temperature', 'bathroom_type', 'bathroom_status', 'pkg_location', 'pkg_estimate_begin', 'pkg_estimate_end', 'cars_seen', 'people_seen', 'dogs_seen', 'horses_seen')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )
  list_display = ('get_trail', 'get_trailhead', 'day_hiked', 'date_hiked')
  list_filter = ['trail', 'trail__region']
  
admin.site.register(Region, RegionAdmin)
admin.site.register(Trail, TrailAdmin)
admin.site.register(Trailhead, TrailheadAdmin)
admin.site.register(Report, ReportAdmin)
