from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('regions/', views.regions, name='regions'),

  path('list/', views.trail_list, name='trail_list'),
  path('reports/', views.reports_list, name='reports_list'),
  path('reports/day/<str:day>', views.reports_day, name='reports_day'),
  path('reports/time/<str:period>', views.reports_time, name='reports_time'),

  path('<slug:region_slug>/', views.trails, name='trails'),
  path('<slug:region_slug>/<slug:trail_slug>/', views.trailheads, name='trailheads'),

  #TODO
  path('<slug:region_slug>/<slug:trail_slug>/summary', views.trail_summary, name='trail_summary'),
  #

  path('<slug:region_slug>/trailheads/bathroom/', views.trailheads_filter_bathroom, name='trailheads_filter_bathroom'),
  path('<slug:region_slug>/trailheads/access/', views.trailheads_filter_access, name='trailheads_filter_access'),
  
  path('<slug:region_slug>/<slug:trailhead_slug>/reports', views.reports_trailhead, name='reports_trailhead'),
  path('<slug:region_slug>/<slug:trail_slug>/reports/', views.reports_trail, name='reports_trail'),
  path('<slug:region_slug>/<slug:trail_slug>/<slug:trailhead_slug>/reports/', views.reports_trail_trailhead, name='reports_trail_trailhead'),

  path('<slug:region_slug>/<slug:trail_slug>/<slug:trailhead_slug>/<str:report>/', views.report, name='report'),

  path('<slug:region_slug>/<slug:trail_slug>/filtering/', views.reports_filter, name='reports_filter'),
  path('<slug:region_slug>/<slug:trail_slug>/day/<str:day>', views.reports_trail_day, name='reports_trail_day'),
  path('<slug:region_slug>/<slug:trail_slug>/time/<str:period>', views.reports_trail_time, name='reports_trail_time')
]