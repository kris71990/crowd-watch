from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('regions/', views.regions, name='regions'),

  path('list/', views.trail_list, name='trail_list'),
  path('reports/', views.reports_list, name='reports_list'),
  # TODO 
  path('reports/day/<str:day>', views.reports_day, name='reports_day'),
  path('reports/time/<str:period>', views.reports_time, name='reports_time'),
  #

  path('<str:region>/', views.trails, name='trails'),
  path('<str:region>/<str:trail>/', views.trailheads, name='trailheads'),

  path('<str:region>/<str:trail>/reports/', views.reports_trail, name='reports_trail'),
  path('<str:region>/<str:trail>/<str:trailhead>/reports/', views.reports_trailhead, name='reports_trailhead'),

  path('<str:region>/<str:trail>/<str:trailhead>/<str:report>/', views.report, name='report'),

  # TODO
  # path('<str:region>/<str:trail>/reports/<str:day>')
  #
]