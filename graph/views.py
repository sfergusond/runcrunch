from django.http import HttpResponse
from django.views.decorators.http import require_POST

from app.models import Athlete
from .utils.getPolyline import getStreamsFromPolyline
from .graphs.paceElevGraph import paceElevGraph
from .graphs.model3DGraph import model3DGraph
from .graphs.mapThumbnailGraph import mapThumbnail
from .graphs.gradeZonesGraph import gradeZonesGraph
from .graphs.dashboardTable import dashboardTable
from .graphs.dashboardBarChart import dashboardBarChart
from .graphs.heatmap import heatmap

import json
import datetime

@require_POST
def getPaceElevGraph(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  graph = paceElevGraph(
    activity['streams']['distanceStream'],
    activity['streams']['paceStream'],
    activity['streams']['adjustedPaceStream'],
    activity['streams']['elevationStream'],
    activity['streams']['hrStream'],
    athlete
  )
  return HttpResponse(graph)

@require_POST
def get3DModelGraph(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  graph = model3DGraph(activity, athlete)
  return HttpResponse(graph)

@require_POST
def getMapThumbnail(request):
  activity = json.loads(request.body)
  graph = mapThumbnail(
    activity['streams']['latStream'],
    activity['streams']['lngStream']
  )
  return HttpResponse(graph)

@require_POST
def getGradeZonesGraph(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  graph = gradeZonesGraph(activity, athlete)
  return HttpResponse(graph)

@require_POST
def getHeatmap(request):
  athleteId = json.loads(request.body)['athlete']
  athlete = Athlete.objects.get(pk=athleteId)
  latStream, lngStream = getStreamsFromPolyline(athlete)
  graph = heatmap(latStream, lngStream)
  return HttpResponse(graph)

@require_POST
def getDashboardTable(request):
  data = json.loads(request.body)
  athlete = Athlete.objects.get(pk=data['athlete'])
  fromDate = datetime.datetime.strptime(data['fromDate'], '%Y-%m-%d')
  toDate = datetime.datetime.strptime(data['toDate'], '%Y-%m-%d')
  table = dashboardTable(fromDate, toDate, athlete)
  return HttpResponse(table)

@require_POST
def getDashboardBarChart(request):
  data = json.loads(request.body)
  athlete = Athlete.objects.get(pk=data['athlete'])
  fromDate = datetime.datetime.strptime(data['fromDate'], '%Y-%m-%d')
  toDate = datetime.datetime.strptime(data['toDate'], '%Y-%m-%d')
  metric = data['metric']
  graph = dashboardBarChart(athlete, metric, fromDate, toDate)
  return HttpResponse(graph)
