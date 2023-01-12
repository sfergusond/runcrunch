import datetime
import pandas as pd

from app.models import Activity

def getActivityDataFrame(athlete, fromDate, toDate, values, type='Run'):
  activities = Activity.objects.filter(
    athlete=athlete
  ).filter(
    timestamp__gte=fromDate
  ).filter(
    timestamp__lte=toDate + datetime.timedelta(days=1)
  ).filter(
    type__contains=type
  ).values(*values)
  df = pd.DataFrame(activities)
  if 'timestamp' in values:
    df.timestamp = pd.to_datetime(df.timestamp)
  return df