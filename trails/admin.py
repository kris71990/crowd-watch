from django.contrib import admin
from .models import Trail

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

admin.site.register(Trail, TrailAdmin)
