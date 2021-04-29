from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('regions/', views.regions, name='regions'),
  # trails/<region>
  path('<str:region>/', views.trails, name='trails'),
  # trails/<region>/<trail>
  path('<str:region>/<str:trail>/', views.trailheads, name='trailheads'),
  # trails/<region>/<trail>/reports
  path('<str:region>/<str:trail>/reports/', views.reports_trail, name='reports_trail'),
  # trails/<region>/<trail>/<trailhead>/reports
  path('<str:region>/<str:trail>/<str:trailhead>/', views.reports_trailhead, name='reports_trailhead')
]