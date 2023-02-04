from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST

from app.models import Athlete
from .utils.getPolyline import getStreamsFromPolyline
from .utils.getLaps import getDeviceLaps, getAutoLaps, getSkiRuns
from .graphs.paceElevGraph import paceElevGraph
from .graphs.model3DGraph import model3DGraph
from .graphs.mapThumbnailGraph import mapThumbnail
from .graphs.annotatedMap import annotatedMap
from .graphs.paceZonesGraph import paceZonesGraph
from .graphs.skiSpeedZonesGraph import skiSpeedZonesGraph
from .graphs.gradeZonesGraph import gradeZonesGraph
from .graphs.lapsBarChart import lapsBarChart
from .graphs.dashboardTable import dashboardTable
from .graphs.dashboardBarChart import dashboardBarChart
from .graphs.dashboardScheduleChart import dashboardScheduleChart
from .graphs.trendsBarChart import trendsBarChart

import json
import datetime
import boto3

@require_POST
def getPaceElevGraph(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  graph = paceElevGraph(activity, athlete)
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
def getAnnotatedMap(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  graph = annotatedMap(athlete, activity)
  return HttpResponse(graph)

@require_POST
def getPaceZonesGraph(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  if activity['isAmbulatory']:
    graph = paceZonesGraph(activity, athlete)
  else:
    graph = skiSpeedZonesGraph(activity, athlete)
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
  client = boto3.client(
    's3',
    region_name=settings.AWS_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
  )
  obj = client.get_object(
    Bucket=settings.AWS_HEATMAP_BUCKET_NAME,
    Key=f'heatmap-graph-html-{athlete.id}.html'
  )
  graph = obj['Body'].read().decode('utf-8')
  return HttpResponse(graph)

@require_POST
def getlapsBarChartDevice(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  laps = getDeviceLaps(activity, athlete)
  graph = lapsBarChart(activity, laps, athlete)
  return HttpResponse(graph)

@require_POST
def getlapsBarChartAuto(request):
  activity = json.loads(request.body)
  athlete = Athlete.objects.get(pk=activity['fields']['athlete'])
  if activity['isAmbulatory']:
    laps = getAutoLaps(activity, athlete)
  else:
    laps = getSkiRuns(activity, athlete)
  graph = lapsBarChart(activity, laps, athlete)
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

@require_POST
def getDashboardScheduleChart(request):
  data = json.loads(request.body)
  athlete = Athlete.objects.get(pk=data['athlete'])
  fromDate = datetime.datetime.strptime(data['fromDate'], '%Y-%m-%d')
  toDate = datetime.datetime.strptime(data['toDate'], '%Y-%m-%d')
  graph = dashboardScheduleChart(athlete, fromDate, toDate)
  return HttpResponse(graph)

@require_POST
def getTrendsBarChart(request):
  data = json.loads(request.body)
  athlete = Athlete.objects.get(pk=data['athlete'])
  period = data['period']
  metric = data['metric']
  graph = trendsBarChart(athlete, metric, period)
  return HttpResponse(graph)
