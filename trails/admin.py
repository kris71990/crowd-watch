from django.contrib import admin
from .models import Trail, Trailhead, Report

class TrailAdmin(admin.ModelAdmin):
  readonly_fields = ('id', 'modified')
  fieldsets = (
    (None, {
      'fields': ('name', 'region', 'coordinates', 'length', 'elevation_gain')
    }),
    ('Metadata', {
      'fields': readonly_fields
    })
  )

class TrailheadAdmin(admin.ModelAdmin):
  readonly_fields = ('id', 'trail', 'modified')
  fieldsets = (
    ('For Trail: ', {
      'fields': ('trail',)
    }),
    (None, {
      'fields': ('name', 'coordinates', 'pkg_type', 'pkg_capacity', 'bathroom')
    }),
    ('Metadata', {
      'fields': ('id', 'modified')
    })
  )

class ReportAdmin(admin.ModelAdmin):
  readonly_fields = ('id', 'trail', 'trailhead', 'modified')
  fieldsets = (
    ('For Trail', {
      'fields': ('trail', 'trailhead')
    }),
    (None, {
      'fields': ('date_hiked', 'day_hiked', 'trail_begin', 'trail_end', 'bathroom', 'pkg_location', 'pkg_estimate_begin', 'pkg_estimate_end', 'cars_seen', 'people_seen', 'dogs_seen', 'horses_seen'),
    }),
    ('Metadata', {
      'fields': ('id', 'modified')
    })
  )
  

admin.site.register(Trail, TrailAdmin)
admin.site.register(Trailhead, TrailheadAdmin)
admin.site.register(Report, ReportAdmin)
