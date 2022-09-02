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
  dateIsNotMax = toDate != datetime.date.max
  unitPref = athlete.unitPreference
  activities = Activity.objects.filter(
    athlete=athlete
  ).filter(
    timestamp__gte=fromDate
  ).filter(
    timestamp__lte=toDate + datetime.timedelta(days=int(dateIsNotMax))
  )
  count = activities.count()
  
  if count:
    distance = activities.aggregate(Sum('distance'))['distance__sum']
    time = activities.aggregate(Sum('time'))['time__sum']
    pace = distance / time
    elevation = activities.aggregate(Sum('elevation'))['elevation__sum']
    heartrate = activities.aggregate(Avg('averageHr'))['averageHr__avg']

    stats = {
      'count': count,
      'distance': distanceFriendly(distance, unitPref),
      'time': timeFriendly(time),
      'pace': speedToPace(pace, unitPref),
      'elevation': elevationFriendly(elevation, unitPref),
      'heartrate': round(heartrate)
    }
    
    return stats
