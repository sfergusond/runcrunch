from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import DateForm, PersonalRecord, UnitPreference, RegisterForm
from .models import Athlete, Activity
from .utils.callImporter import callImporter
from .utils.getActivityStatsForPeriod import getActivityStatsForPeriod
from utils.calendar import getNextSunday
from graph.utils.getLaps import (
  getLapsTable,
  getDeviceLaps,
  getAutoLaps,
  getSkiRuns,
  getSkiRunsTable
)

import datetime
import json

def home(request):
  if request.user.is_authenticated:
    return redirect(reverse('dashboard'))
  return render(request, 'pages/landingPage.html')

def register(request):
  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
      form.save()
      username=form.cleaned_data['username']
      new_user = authenticate(
        username=username,
        password=form.cleaned_data['password1']
        )
      login(request, new_user)
      Athlete.objects.create(user=request.user)
      return redirect('connectToStrava')
  else:
      form = RegisterForm()
  return render(
    request,
    'pages/register.html',
    {
      'form': form
    }
  )

@login_required
def connect_to_strava(request):
  queryString = dict(request.GET.items())
  if 'activity:read' in queryString.get('scope', ''):
    code = queryString.get('code')
    request.athlete.stravaAuthenticate(code)
    return redirect('account')
  
  redirectUrl = (
    'https://www.strava.com/oauth/authorize?' +
    f'client_id={settings.STRAVA_CLIENT_ID}&' +
    f'redirect_uri={settings.DOMAIN}/connect-to-strava&' +
    '&approval_prompt=auto&response_type=code&scope=activity%3Aread%2Cactivity%3Aread_all'
    )
  return render(
    request,
    'pages/connectToStrava.html',
    {
      'redirectUrl': redirectUrl
    }
  )

@login_required
def account(request):
  if request.method == 'POST':
    prForm = PersonalRecord(request.POST)
    unitPreference = UnitPreference(request.POST)
    if 'import' in request.POST:
      callImporter(request)
    if 'prForm' in request.POST:
      if prForm.is_valid():
        prForm.save(request.athlete)
    if 'unitPref' in request.POST:
      if unitPreference.is_valid():
        unitPreference.save(request.athlete)
  else:
    prForm = PersonalRecord()
    unitPreference = UnitPreference({
      'metric': request.athlete.unitPreference
    })
  accountStats = getActivityStatsForPeriod(
    datetime.date.min,
    datetime.date.max,
    request.athlete
  )
  return render(
    request,
    'pages/account.html',
    {
      'prForm': prForm,
      'unitPreference': unitPreference,
      'accountStats': accountStats
    }
  )

@login_required
def dashboard(request):
  toDate = getNextSunday().date()
  fromDate = toDate - datetime.timedelta(days=20)
  if request.method == 'POST':
    dateForm = DateForm(request.POST)
    if dateForm.is_valid():
      formData = dateForm.cleaned_data
      fromDate = min(formData['fromDate'], formData['toDate'])
      toDate = max(formData['fromDate'], formData['toDate'])
  else:
    dateForm = DateForm({
      'fromDate': fromDate,
      'toDate': toDate
    })
  periodStats = getActivityStatsForPeriod(fromDate, toDate, request.athlete)
  lastSevenStats = getActivityStatsForPeriod(
    datetime.datetime.today() - datetime.timedelta(days=6),
    datetime.datetime.today(),
    request.athlete
  )
  return render(
    request,
    'pages/dashboard.html',
    {
      'dateForm': dateForm,
      'fromDate': fromDate,
      'toDate': toDate,
      'periodStats': periodStats,
      'lastSevenStats': lastSevenStats
    }
  )

@login_required
def viewActivity(request, activityId):
  activity = Activity.objects.get(pk=activityId)
  if activity.athlete != request.athlete:
    return HttpResponse(status=403)
  
  activity.getStreams()
  activity.getFriendlyStats()
  activityJson = activity.toJson()
  activityJsonDict = json.loads(activityJson)
  deviceLaps = getDeviceLaps(activityJsonDict, request.athlete)
  
  if activity.isAmbulatory():
    autoLaps = getAutoLaps(activityJsonDict, request.athlete)
    deviceLapsTable = getLapsTable(deviceLaps, request.athlete.unitPreference)
    autoLapsTable = getLapsTable(autoLaps, request.athlete.unitPreference)
  else:
    autoLaps = getSkiRuns(activityJsonDict, request.athlete)
    deviceLapsTable = getSkiRunsTable(deviceLaps, request.athlete.unitPreference)
    autoLapsTable = getSkiRunsTable(autoLaps, request.athlete.unitPreference)
      
  return render(
    request,
    'pages/viewActivity.html',
    {
      'activity': activity,
      'activityJson': activityJson,
      'autoLapsTable': autoLapsTable,
      'deviceLapsTable': deviceLapsTable
    }
  )
