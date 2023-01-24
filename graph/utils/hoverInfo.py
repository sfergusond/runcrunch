from utils.convert import speedToPace, speedFriendly

def getDistanceHoverInfo(stream, unitPref):
  return list(map(
    lambda x : f'{round(x, 2)} ' + ('mi' if unitPref == 'I' else 'km'), stream
  ))

def getPaceHoverInfo(stream, unitPref):
  return list(map(
    lambda x : speedToPace(x, unitPref) + (' /mi' if unitPref == 'I' else ' /km'),
    stream
  ))
  
def getSpeedHoverInfo(stream, unitPref):
  return list(map(lambda x : speedFriendly(x, unitPref), stream))  

def getElevationHoverInfo(stream, unitPref):
  return list(map(
    lambda x : f'{round(x)} ' + ('ft' if unitPref == 'I' else 'm'), stream
  ))
  
def getHrHoverInfo(stream):
  return list(map(
    lambda x : f'{x} bpm', stream
  ))

def getGradeHoverInfo(stream):
  return list(map(
    lambda x : f'{int(round(x))}%', stream
  ))
