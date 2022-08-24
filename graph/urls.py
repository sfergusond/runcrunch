from django.urls import path

from . import views

urlpatterns = [
  path('paceElevGraph', views.getPaceElevGraph, name='paceElevGraph'),
  path('3DModelGraph', views.get3DModelGraph, name='3DModelGraph'),
  path('mapThumbnail', views.getMapThumbnail, name='mapThumbnail'),
  path('gradeZonesGraph', views.getGradeZonesGraph, name='gradeZonesGraph'),
  path('dashboardBarChart', views.getDashboardBarChart, name='dashboardBarChart'),
  
  path('dashboardTable', views.getDashboardTable, name='dashboardTable'),
  
  path('getHeatmap', views.getHeatmap, name='getHeatmap'),
]