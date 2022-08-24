from django.db.models import Avg, Sum

import datetime

from ..models import Activity
from utils.convert import ( 
  speedToPace, 
  timeFriendly, 
  intensityFriendly, 
  distanceFriendly, 
  elevationFriendly
)

def getActivityStatsForPeriod(fromDate, toDate, athlete):
  unitPref = athlete.unitPreference
  activities = Activity.objects.filter(
    athlete=athlete
  ).filter(
    timestamp__gte=fromDate
  ).filter(
    timestamp__lte=toDate + datetime.timedelta(days=1)
  )
  
  count = activities.count()
  distance = activities.aggregate(Sum('distance'))['distance__sum']
  time = activities.aggregate(Sum('time'))['time__sum']
  pace = distance / time
  elevation = activities.aggregate(Sum('elevation'))['elevation__sum']
  intensity = activities.aggregate(Avg('intensity'))['intensity__avg']
  heartrate = activities.aggregate(Avg('averageHr'))['averageHr__avg']

  stats = {
    'count': count,
    'distance': distanceFriendly(distance, unitPref),
    'time': timeFriendly(time),
    'pace': speedToPace(pace, unitPref),
    'elevation': elevationFriendly(elevation, unitPref),
    'intensity': intensityFriendly(intensity),
    'heartrate': round(heartrate)
  }
  
  return stats
