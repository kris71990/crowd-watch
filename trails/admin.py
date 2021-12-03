from django.contrib import admin
from django.db.models import Count
from .models import Region, Trail, Trailhead, Report

class TrailheadInline(admin.StackedInline):
  model = Trail.trailheads.through

  def get_trail(self, obj):
    return obj.trail.name

  get_trail.short_description = 'Trail'

  fieldsets = (
    ('For Trail', {
      'fields': ('get_trail',)
    }),
    (None, {
      'fields': ('name', 'coordinates', 'access', 'access_distance', 'pkg_type', 'pkg_capacity', 'bathroom_type', 'bathroom_status')
    }),
  )
  extra = 1

class RegionAdmin(admin.ModelAdmin):
  readonly_fields = ['id']

class TrailAdmin(admin.ModelAdmin):
  def get_queryset(self, request):
    return Trail.objects.annotate(trailhead_count=Count('trailhead'))

  def trailhead_count(self, obj):
    return obj.trailhead_count

  trailhead_count.short_description = 'Trailheads'

  readonly_fields = ['id', 'modified']
  fieldsets = (
    (None, {
      'fields': ('name', 'region', 'coordinates', 'length', 'elevation_gain')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )
  inlines = [TrailheadInline]
  list_display = ('name', 'region', 'trailhead_count')
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
admin.site.register(Report, ReportAdmin)
