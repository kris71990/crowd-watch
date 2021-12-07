from django.contrib import admin
from .models import Region, Trail, Trailhead, Report

class RegionAdmin(admin.ModelAdmin):
  readonly_fields = ['id']

class TrailAdmin(admin.ModelAdmin):
  def get_trailheads(self, obj):
    trailheads = []
    for trailhead in obj.trailheads.all():
      trailheads.append(trailhead.name)
    return trailheads

  get_trailheads.short_description = 'Trailheads'

  readonly_fields = ['id', 'modified', 'get_trailheads']
  fieldsets = (
    (None, {
      'fields': ('name', 'region', 'coordinates', 'length', 'elevation_gain')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )
  list_display = ('name', 'region', 'get_trailheads')
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
      'fields': ('trail', 'trailhead')
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
