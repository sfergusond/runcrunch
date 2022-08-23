import datetime
from typing import Callable

CONVERSIONS = {
  'metersToMiles': lambda x: x / 1609.34,
  'metersToFeet': lambda x : x * 3.28084,
  'metersToKm': lambda x: x / 1000,
  'secondsToMins': lambda x: x / 60,
}

def convertStream(stream, conversion, *args):
  if isinstance(conversion, str):
    stream = list(map(lambda x : CONVERSIONS[conversion](x), stream))
  elif isinstance(conversion, Callable):
    stream = list(map(lambda x: conversion(x, *args), stream))
  return stream

def speedToPace(speed, unitType):
  pace = 0
  if not isinstance(speed, float):
    speed = float(speed)
  if speed > 0:
    if unitType == 'I':
      pace = 1 / (
        CONVERSIONS['metersToMiles'](speed) /
        CONVERSIONS['secondsToMins'](1)
      ) 
    else:
      pace = 1 / (
        CONVERSIONS['metersToKm'](speed) /
        CONVERSIONS['secondsToMins'](1)
      )
  pace = minutesFriendly(pace)
  return pace
    
def minutesFriendly(minutes):
  minsFriendly = str(datetime.timedelta(minutes=minutes))
  minsFriendly = minsFriendly[:minsFriendly.find('.')]
  if minutes < 60:
    minsFriendly = minsFriendly.split(':')
    minsFriendly = ':'.join(minsFriendly[1:])
  return minsFriendly

def intensityFriendly(intensity):
  if isinstance(intensity, (int, float)):
    # Makes this more readable
    pct = intensity * 2
    if pct > 200:
      return 'PR Effort'
    elif pct > 190:
      return 'Race/Anaerobic'
    elif pct > 180:
      return 'VO2 Max'
    elif pct > 160:
      return 'Tempo'
    elif pct > 140:
      return 'Threshold'
    elif pct > 115:
      return 'Endurance - Hard'
    elif pct > 85:
      return 'Endurance - Moderate'
    elif pct > 60:
      return 'Endurance - Easy'
    else:
      return 'Recovery'
  return ''