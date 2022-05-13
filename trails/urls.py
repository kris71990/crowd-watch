from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('regions/', views.regions, name='regions'),

  path('list/', views.trail_list, name='trail_list'),
  path('reports/', views.reports_list, name='reports_list'),
  path('reports/day/<str:day>', views.reports_day, name='reports_day'),
  path('reports/time/<str:period>', views.reports_time, name='reports_time'),

  path('<str:region>/', views.trails, name='trails'),
  path('<str:region>/<str:trail>/', views.trailheads, name='trailheads'),

  #TODO
  path('<str:region>/<str:trail>/summary', views.trail_summary, name='trail_summary'),
  #

  path('<str:region>/trailheads/bathroom/', views.trailheads_filter_bathroom, name='trailheads_filter_bathroom'),
  path('<str:region>/trailheads/access/', views.trailheads_filter_access, name='trailheads_filter_access'),

  path('<str:region>/<str:trail>/reports/', views.reports_trail, name='reports_trail'),
  path('<str:region>/<str:trailhead>/region-reports/', views.reports_trailhead, name='reports_trailhead'),

  path('<str:region>/<str:trail>/<str:trailhead>/<str:report>/', views.report, name='report'),

  path('<str:region>/<str:trail>/filtering/', views.reports_filter, name='reports_filter'),
  path('<str:region>/<str:trail>/day/<str:day>', views.reports_trail_day, name='reports_trail_day'),
  path('<str:region>/<str:trail>/time/<str:period>', views.reports_trail_time, name='reports_trail_time')
]