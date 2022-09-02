from django.urls import path

from . import views

urlpatterns = [
  path('paceElevGraph', views.getPaceElevGraph, name='paceElevGraph'),
  path('3DModelGraph', views.get3DModelGraph, name='3DModelGraph'),
  path('mapThumbnail', views.getMapThumbnail, name='mapThumbnail'),
  path('annotatedMap', views.getAnnotatedMap, name='annotatedMap'),
  path('paceZonesGraph', views.getPaceZonesGraph, name='paceZonesGraph'),
  path('gradeZonesGraph', views.getGradeZonesGraph, name='gradeZonesGraph'),
  path('lapsBarChartDevice', views.getlapsBarChartDevice, name='lapsBarChartDevice'),
  path('lapsBarChartAuto', views.getlapsBarChartAuto, name='lapsBarChartAuto'),
  
  path('dashboardBarChart', views.getDashboardBarChart, name='dashboardBarChart'),
  path('dashbardScheduleChart', views.getDashboardScheduleChart, name='dashboardScheduleChart'),
  path('dashboardTable', views.getDashboardTable, name='dashboardTable'),
  
  path('getTrendsBarChart', views.getTrendsBarChart, name='getTrendsBarChart'),
  path('getHeatmap', views.getHeatmap, name='getHeatmap'),
]