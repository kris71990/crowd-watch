from django.contrib import admin
from .models import Trail, Trailhead

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

admin.site.register(Trail, TrailAdmin)
admin.site.register(Trailhead, TrailheadAdmin)
