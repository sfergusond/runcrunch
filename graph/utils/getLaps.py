import pandas as pd
import statistics

from utils.calculateIntensity import calculateIntensity
from utils.convert import (
  distanceFriendly,
  timeFriendly,
  speedToPace,
  intensityFriendly,
  elevationFriendly,
  gradeFriendly,
  removeNonMovingFromStream
)

def getTotalElevationGain(elevationStream):
  elevSteps = list(map(
    lambda y, x : y - x, elevationStream[1:], elevationStream[:-1]
  ))
  totalGain = sum([e for e in elevSteps if e > 0])
  return totalGain

def indexOfNearest(target, li):
  f = lambda x : abs(x - target)
  closest = min(li, key=f)
  return li.index(closest)

def getLapDetails(lapStreams, athlete):
  lap = {}
  if lapStreams.get('distanceStream'):
    lap['distance'] = lapStreams['distanceStream'][-1] - lapStreams['distanceStream'][0]
    lap['velocity'] = statistics.mean(lapStreams['paceStream'])
    lap['intensity'] = calculateIntensity(athlete, lap['velocity'], lap['distance'])
  if lapStreams.get('timeStream'):
    if lap.get('distance'):
      lap['movingTime'] = lap['distance'] / lap['velocity']
    else:
      lap['movingTime'] = lapStreams['timeStream'][-1] - lapStreams['timeStream'][0]
  if lapStreams.get('hrStream'):
    lap['heartrate'] = statistics.mean(lapStreams['hrStream'])
  if lapStreams.get('adjustedPaceStream'):
    lap['adjustedPace'] = statistics.mean(lapStreams['adjustedPaceStream'])
    lap['intensity'] = calculateIntensity(athlete, lap['adjustedPace'], lap['distance'])
    lap['totalElevationGain'] = getTotalElevationGain(lapStreams['elevationStream'])
    lap['averageGrade'] = statistics.mean(lapStreams['gradeStream'])
    lap['minElevation'] = min(lapStreams['elevationStream'])
    lap['maxElevation'] = max(lapStreams['elevationStream'])
    lap['elevationChange'] = lapStreams['elevationStream'][-1] - lapStreams['elevationStream'][0]
  return lap

def getLapStreams(streams, lap):
  lapStreams = {
    'movingStream': streams.get('movingStream')
  }
  if streams.get('distanceStream'):
    lapStreams['distanceStream'] = streams['distanceStream'][lap['startIndex'] : lap['endIndex']]
    lapStreams['timeStream']= streams['timeStream'][lap['startIndex'] : lap['endIndex']]
    lapStreams['paceStream'] = streams['paceStream'][lap['startIndex'] : lap['endIndex']]
  if streams.get('adjustedPaceStream'):
    lapStreams['adjustedPaceStream'] = streams['adjustedPaceStream'][lap['startIndex'] : lap['endIndex']]
    lapStreams['elevationStream'] = streams['elevationStream'][lap['startIndex'] : lap['endIndex']]
    lapStreams['gradeStream'] = streams['gradeStream'][lap['startIndex'] : lap['endIndex']]
  if streams.get('hrStream'):
    lapStreams['hrStream'] = streams['hrStream'][lap['startIndex'] : lap['endIndex']]
  return lapStreams

def getDeviceLaps(activity, athlete):
  laps = []
  for lap in activity.get('laps', []):
    if activity.get('streams'):
      lapStreams = getLapStreams(activity['streams'], lap)
      for key, stream in lapStreams.items():
        if key != 'movingStream':
          lapStreams[key] = removeNonMovingFromStream(
            stream,
            lapStreams['movingStream']
          )
      newLap = getLapDetails(lapStreams, athlete)
      if lap.get('distance'):
        laps.append(newLap)
  return laps

def getAutoLaps(activity, athlete, retIndices=False):
  if activity.get('streams'):
    laps, lapIndices = [], []
    unitPref = athlete.unitPreference
    step = 1609.34 if unitPref == 'I' else 1000
    numLaps = int(activity['fields']['distance'] / step + 1)
    streams = activity['streams']
    movingStream = streams['movingStream'].copy()
    
    for stream in streams:
      map(lambda s : removeNonMovingFromStream(s, movingStream), stream)
    
    for i in range(numLaps + 1):
      target = i * step
      lapIndex = indexOfNearest(target, streams['distanceStream'])
      lapIndices.append(lapIndex)
    if retIndices:
      return lapIndices
      
    for i in range(numLaps):
      lap = {
        'startIndex': lapIndices[i],
        'endIndex': lapIndices[i + 1] + 1
      }
      lapStreams = getLapStreams(streams, lap)
      lap = getLapDetails(lapStreams, athlete)
      laps.append(lap)
    return laps
      
def getLapsTable(laps, unitPref):
  df = pd.DataFrame(laps)
  df.reset_index(inplace=True)
  if not len(df):
    return ''
  
  df['index'] = df['index'].apply(lambda x : x + 1)
  df.distance = df.distance.apply(lambda x : distanceFriendly(x, unitPref))
  df.movingTime = df.movingTime.apply(lambda x : timeFriendly(x))
  df.velocity = df.velocity.apply(lambda x : speedToPace(x, unitPref))
  df.adjustedPace = df.adjustedPace.apply(lambda x : speedToPace(x, unitPref))
  df.heartrate = df.heartrate.apply(lambda x : round(x) if not pd.isna(x) else '')
  df.intensity = df.intensity.apply(
    lambda x : f'{round(x)}% ({intensityFriendly(x)})' if not pd.isna(x) else ''
  )
  df.totalElevationGain = df.totalElevationGain.apply(lambda x : elevationFriendly(x, unitPref))
  df.minElevation = df.minElevation.apply(lambda x : elevationFriendly(x, unitPref))
  df.maxElevation = df.maxElevation.apply(lambda x : elevationFriendly(x, unitPref))
  df.elevationChange = df.elevationChange.apply(lambda x : elevationFriendly(x, unitPref))
  df.averageGrade = df.averageGrade.apply(lambda x : gradeFriendly(x))
  
  df = df[[
    'index',
    'distance',
    'movingTime',
    'velocity',
    'adjustedPace',
    'heartrate',
    'intensity',
    'totalElevationGain',
    'elevationChange',
    'minElevation',
    'maxElevation',
    'averageGrade'
  ]]
  
  dfHtml = df.to_html(index=False, escape=False)
  dfHtml = dfHtml[dfHtml.find('<tbody>') : dfHtml.find('</tbody>')] + '</tbody>'
  dfHtml = dfHtml.replace('<tr>0</tr>', '<tr></tr>').replace('NaN', '')
  return dfHtml