from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core import serializers

import stravalib
from stravalib import unithelper
import time
import statistics
import json

from utils import convert
from utils.adjustedPace import getPaceMultiplier

class Athlete(models.Model):
  stravaId = models.IntegerField(
    null=True,
    blank=True
  )
  accessToken = models.CharField(
    max_length=100,
    blank=True
  )
  tokenExpiration = models.IntegerField(
    null=True,
    blank=True
  )
  refreshToken = models.CharField(
    max_length=100,
    blank=True
  )
  prDistance = models.IntegerField(
    default=1000
  )
  prTime = models.IntegerField(
    default=60*5
  )
  unitPreference = models.CharField(
    max_length=1,
    choices=(
      ('M', 'Metric'),
      ('I', 'Imperial'),
    ),
    default='I'
  )
  user = models.ForeignKey(
    User, 
    on_delete=models.CASCADE
  )
  
  def stravaAuthenticate(self, code):
    codes = stravalib.Client().exchange_code_for_token(
      settings.STRAVA_CLIENT_ID,
      settings.STRAVA_CLIENT_SECRET,
      code
    )
    client = stravalib.Client(access_token=codes['access_token'])
    stravaAthlete = client.get_athlete()
    self.stravaId = stravaAthlete.id
    self.accessToken = codes['access_token']
    self.tokenExpiration = codes['expires_at']
    self.refreshToken = codes['refresh_token']
    self.save()
    
  def stravaReauthenticate(self):
    if self.stravaId and time.time() > self.tokenExpiration:
      client = stravalib.Client()
      codes = client.refresh_access_token(
        settings.STRAVA_CLIENT_ID,
        settings.STRAVA_CLIENT_SECRET,
        self.refreshToken
      )
      self.accessToken = codes['access_token']
      self.refreshToken = codes['refresh_token']
      self.tokenExpiration = codes['expires_at']
      self.save()
      
  def getEasyPace(self):
    prPace = self.prDistance / self.prTime
    easyPace = (
      prPace * (
        convert.CONVERSIONS['metersToMiles'](self.prDistance)**0.07
      )
    ) / 2.25
    return easyPace
  
  def getRelativePrPace(self, distance):
    prPace = self.prDistance / self.prTime
    relativePace = (prPace * ((self.prDistance/distance)**0.07))
    return relativePace
  
  def getPrFriendly(self):
    time = convert.speedToPace(
      self.prDistance / self.prTime,
      self.unitPreference
    )
    distance = convert.distanceFriendly(
      self.prDistance,
      self.unitPreference
    )
    return f'{time} for {distance}'
  
class Activity(models.Model):
  id = models.BigAutoField(
    primary_key=True
  )
  stravaId = models.BigIntegerField(
    unique=True
  )
  averageHr = models.IntegerField(
    null=True,
    blank=True
  )
  timestamp = models.DateTimeField()
  distance = models.IntegerField()
  time = models.IntegerField()
  elevation = models.IntegerField(
    null=True,
    blank=True
  )
  intensity = models.DecimalField(
    max_digits=20,
    decimal_places=2,
    null=True,
    blank=True
  )
  title = models.CharField(
    max_length=500
  )
  startLat = models.DecimalField(
    decimal_places=16,
    max_digits=25,
    null=True,
    blank=True
  )
  startLng = models.DecimalField(
    decimal_places=16,
    max_digits=25,
    null=True,
    blank=True
  )
  athlete = models.ForeignKey(
    Athlete,
    on_delete=models.CASCADE
  )
  
  def calculateIntensity(self, adjustedSpeed=None):
    athlete = self.athlete
    if not athlete.prDistance or not athlete.prTime:
      return None
    easyPace = 2.06 # 13 min/mile
    if not adjustedSpeed:
      speed = self.distance / self.time
    else:
      speed = adjustedSpeed
    speed = speed - easyPace
    prSpeed = athlete.prDistance / athlete.prTime
    prEffort = (
      prSpeed * (
        (athlete.prDistance / self.distance) ** 0.07
        )
      ) - easyPace
    intensity = round((speed/prEffort) * 100, 2)
    self.intensity = intensity
    self.save()
    return intensity

  def getFriendlyStats(self):
    unitPref = self.athlete.unitPreference
    convertImperial = unitPref == 'I'
    client = stravalib.Client(access_token=self.athlete.accessToken)
    stravaActivity = client.get_activity(self.stravaId)
    self.description = stravaActivity.description
    self.distanceFriendly = (
      unithelper.miles(stravaActivity.distance) if convertImperial 
      else unithelper.kilometers(stravaActivity.distance)
    )
    self.timeFriendly = stravaActivity.moving_time
    self.elevationFriendly = (
      unithelper.feet(stravaActivity.total_elevation_gain) if convertImperial
      else round(stravaActivity.total_elevation_gain)
    )
    self.paceFriendly = convert.speedToPace(stravaActivity.average_speed, unitPref)
    if self.hasStreams:
      try:
        adjustedSpeed = statistics.mean(self.adjustedPaceStream)
        self.adjustedPaceFriendly = convert.speedToPace(adjustedSpeed, unitPref)
        self.intensity = self.calculateIntensity(adjustedSpeed=adjustedSpeed)
      except Exception as e:
        print(e)
        pass
    self.intensityFriendly = convert.intensityFriendly(self.intensity)
    
  def getStreams(self):
    self.hasStreams = False
    streamTypes = [
      'distance',
      'velocity_smooth',
      'grade_smooth',
      'altitude',
      'latlng',
      'heartrate'
    ]
    client = stravalib.Client(access_token=self.athlete.accessToken)
    streams = client.get_activity_streams(self.stravaId, types=streamTypes)
    if streams:
      self.hasStreams = True
      self.distanceStream = streams.get('distance', {}).to_dict().get('data', [])
      streamLen = len(self.distanceStream)
      getNoneStream = lambda k : ([(None, None)] if k == 'latlng' else [None]) * streamLen
      getStream = lambda k : streams.get(k, {}).to_dict().get('data', getNoneStream(k))
      self.paceStream = getStream('velocity_smooth')
      self.gradeStream = getStream('grade_smooth')
      self.elevationStream = getStream('altitude')
      self.hrStream = getStream('heartrate')
      latlngStream = getStream('latlng')
      self.latStream = [i[0] for i in latlngStream]
      self.lngStream = [i[1] for i in latlngStream]
      self.adjustedPaceStream = getNoneStream('')
      if {'grade_smooth', 'velocity_smooth', 'altitude'}.issubset(streams.keys()):
        self.adjustedPaceStream = list(
          map(
            lambda g, v, e : getPaceMultiplier(g, e) * v,
            self.gradeStream, self.paceStream, self.elevationStream
          )
        )
    return streams
  
  def toJson(self):
    serialized = serializers.serialize('json', [self])
    serialized = json.loads(serialized)[0]
    if getattr(self, 'hasStreams', False):
      streams = {k:v for k, v in self.__dict__.items() if 'Stream' in k}
      serialized['streams'] = streams
    serialized = json.dumps(serialized)
    return serialized
    