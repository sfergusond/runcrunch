import datetime
import pandas as pd

CONVERSIONS = {
  'metersToMiles': lambda x: x / 1609.34,
  'metersToFeet': lambda x : x * 3.28084,
  'metersToKm': lambda x: x / 1000,
  'secondsToMins': lambda x: x / 60,
  'kmToMeters': lambda x : x * 1000,
  'milesToMeters': lambda x : x * 1609.34
}

def convertStream(stream, conversion):
  stream = list(map(lambda x : CONVERSIONS[conversion](x), stream))
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
  pace = timeFriendly(pace, precision='minutes')
  return pace
    
def timeFriendly(time, precision='seconds'):
  if precision == 'seconds':
    timeFriendly = str(datetime.timedelta(seconds=time))
  elif precision == 'minutes':
    timeFriendly = str(datetime.timedelta(minutes=time))
  if '.' in timeFriendly:
    timeFriendly = timeFriendly[:timeFriendly.find('.')]
  if time / (60 if precision == 'seconds' else 1) < 60:
    timeFriendly = timeFriendly.split(':')
    timeFriendly = ':'.join(timeFriendly[1:])
  return timeFriendly

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

def distanceFriendly(distance, unitPref):
  if unitPref == 'I':
    distance = round(CONVERSIONS['metersToMiles'](distance), 2)
    distance = f'{distance} mi'
    return distance
  else:
    distance = round(CONVERSIONS['metersToKm'](distance), 2)
    distance = f'{distance} km'
    return distance
  
def elevationFriendly(elevation, unitPref):
  if not elevation or pd.isna(elevation):
    return ''
  if unitPref == 'I':
    elevation = round(CONVERSIONS['metersToFeet'](elevation))
    elevation = f'{elevation} ft'
    return elevation
  else:
    elevation = round(elevation)
    elevation = f'{elevation} m'
    return elevation
