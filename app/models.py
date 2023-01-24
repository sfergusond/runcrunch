from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core import serializers

import stravalib
from stravalib import unithelper
import time
import statistics
import json

from utils.convert import (
  CONVERSIONS,
  speedToPace,
  distanceFriendly,
  intensityFriendly,
  speedFriendly,
  elevationFriendly,
  removeNonMovingFromStream
)
from utils.adjustedPace import getPaceMultiplier
from utils.calculateIntensity import calculateIntensity

AMBULATORY_TYPES = {
  'Run',
  'Walk',
  'TrailRun',
  'Hike',
  'Snowshoe',
  'VirtualRun,'
}

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
        CONVERSIONS['metersToMiles'](self.prDistance)**0.07
      )
    ) / 2.25
    return easyPace
  
  def getRelativePrPace(self, distance):
    prPace = self.prDistance / self.prTime
    relativePace = (prPace * ((self.prDistance / distance) ** 0.07))
    return relativePace
  
  def getPrFriendly(self):
    time = speedToPace(
      self.prDistance / self.prTime,
      self.unitPreference
    )
    distance = distanceFriendly(
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
  title = models.CharField(
    max_length=500
  )
  type = models.CharField(
    max_length=20,
    default='Run'
  )
  athlete = models.ForeignKey(
    Athlete,
    on_delete=models.CASCADE
  )

  def getFriendlyStats(self):
    isAmbulatory = self.isAmbulatory()
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
    
    self.elevationFriendly = elevationFriendly(
      stravaActivity.total_elevation_gain.get_num(), 
      unitPref
    )
    
    if self.hasStreams:
      calculatedPace = statistics.mean(
        removeNonMovingFromStream(self.paceStream, self.movingStream)
      )
      
      if isAmbulatory:
        adjustedPace = statistics.mean(
          removeNonMovingFromStream(self.adjustedPaceStream, self.movingStream)
        )
        self.paceFriendly = speedToPace(calculatedPace, unitPref)
        self.adjustedPaceFriendly = speedToPace(adjustedPace, unitPref)
        self.intensity = calculateIntensity(self.athlete, adjustedPace, self.distance)
        self.intensityFriendly = intensityFriendly(self.intensity)
      else:
        self.paceFriendly = speedFriendly(calculatedPace, unitPref)
      
        
      self.laps = [{
        'startIndex': lap.start_index,
        'endIndex': lap.end_index,
        'time': lap.moving_time.seconds,
        'distance': int(lap.distance),
        'elevation': int(lap.total_elevation_gain) if lap.total_elevation_gain else None,
        'velocity': float(lap.average_speed),
        'heartrate': float(lap.average_heartrate) if lap.average_heartrate else None,
        'index': lap.lap_index
      } for lap in stravaActivity.laps]
    else:
      if isAmbulatory:
        self.paceFriendly = speedToPace(stravaActivity.average_speed, unitPref)
        self.intensity = calculateIntensity(
          self.athlete,
          self.distance / self.time,
          self.distance
        )
        self.intensityFriendly = intensityFriendly(self.intensity)
      else:
        self.paceFriendly = speedFriendly(stravaActivity.average_speed, unitPref)
    
  def getStreams(self):
    self.hasStreams = False
    streamTypes = [
      ('distance', 'distance'),
      ('velocity_smooth', 'pace'),
      ('time', 'time'),
      ('grade_smooth', 'grade'),
      ('altitude', 'elevation'),
      ('latlng', 'latlng'),
      ('heartrate', 'hr'),
      ('moving', 'moving'),
    ]
    client = stravalib.Client(access_token=self.athlete.accessToken)
    streams = client.get_activity_streams(
      self.stravaId,
      types=[t[0] for t in streamTypes]
    )
    if streams:
      self.hasStreams = True
      getStream = lambda k : streams.get(k).to_dict().get('data') if streams.get(k) else None
      for type, attrName in streamTypes:
        if type == 'latlng':
          latlngStream = getStream('latlng')
          setattr(self, 'latStream', [i[0] for i in latlngStream])
          setattr(self, 'lngStream', [i[1] for i in latlngStream])
        setattr(self, f'{attrName}Stream', getStream(type))
      self.adjustedPaceStream = None
      if {'grade_smooth', 'velocity_smooth', 'altitude'}.issubset(streams.keys()):
        self.adjustedPaceStream = list(
          map(
            lambda g, v, e : getPaceMultiplier(g, e) * v,
            self.gradeStream, self.paceStream, self.elevationStream
          )
        )
    return streams
  
  def isAmbulatory(self):
    """
    Returns true if activity is self-powered on foot (i.e. walks/runs)
    """
    return True if self.type in AMBULATORY_TYPES else False
  
  def toJson(self):
    self.isAmbulatory()
    serialized = serializers.serialize('json', [self])
    serialized = json.loads(serialized)[0]
    if getattr(self, 'hasStreams', False):
      streams = {k:v for k, v in self.__dict__.items() if 'Stream' in k}
      serialized['streams'] = streams
    if getattr(self, 'laps', False):
      serialized['laps'] = self.laps
    serialized['isAmbulatory'] = self.isAmbulatory()
    serialized = json.dumps(serialized)
    return serialized
    