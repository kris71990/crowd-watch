from django.contrib import admin
from django import forms
from .models import Trail, Trailhead, Report

class TrailheadInline(admin.StackedInline):
  model = Trailhead
  readonly_fields = ('id', 'get_trail', 'modified')

  def get_trail(self, obj):
    return obj.trail.name

  get_trail.short_description = 'Trail'

  fieldsets = (
    ('For Trail', {
      'fields': ('get_trail',)
    }),
    (None, {
      'fields': ('name', 'coordinates', 'pkg_type', 'pkg_capacity', 'bathroom')
    }),
    ('Metadata', {
      'fields': ('id', 'modified')
    })
  )
  extra = 1

class TrailAdmin(admin.ModelAdmin):
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
  list_display = ('name', 'region')
  list_filter = ['region', 'modified']

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
      'fields': ('date_hiked', 'day_hiked', 'trail_begin', 'trail_end', 'bathroom', 'pkg_location', 'pkg_estimate_begin', 'pkg_estimate_end', 'cars_seen', 'people_seen', 'dogs_seen', 'horses_seen')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )
  list_display = ('get_trail', 'get_trailhead', 'day_hiked', 'date_hiked')
  list_filter = ['trail']
  

admin.site.register(Trail, TrailAdmin)
admin.site.register(Report, ReportAdmin)
