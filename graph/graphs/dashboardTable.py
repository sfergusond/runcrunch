import datetime
from django.shortcuts import reverse

import pandas as pd

from app.models import Activity
from utils.convert import (
  distanceFriendly,
  timeFriendly,
  elevationFriendly,
  speedToPace
)

def dashboardTable(fromDate, toDate, athlete):
  unitPref = athlete.unitPreference
  activities = Activity.objects.filter(
    athlete=athlete
  ).filter(
    timestamp__gte=fromDate
  ).filter(
    timestamp__lte=toDate + datetime.timedelta(days=1)
  ).values(
    'id',
    'timestamp',
    'title',
    'type',
    'distance',
    'time',
    'elevation',
    'averageHr'
  )
  df = pd.DataFrame(activities)
  df = df.sort_values(by='timestamp', ascending=False)
  df['pace'] = df.distance / df.time
  df.pace = df.pace.apply(
    lambda x : speedToPace(x, unitPref)
  )
  df.timestamp = df.timestamp.apply(
    lambda x : x.strftime('%m/%d/%Y %I:%M %p')
  )
  df.distance = df.distance.apply(
    lambda x : distanceFriendly(x, unitPref)
  )
  df.time = df.time.apply(
    lambda x : timeFriendly(x)
  )
  df.elevation = df.elevation.apply(
    lambda x : elevationFriendly(x, unitPref)
  )
  df.averageHr = df.averageHr.apply(
    lambda x : round(x) if not pd.isna(x) else ''
  )
  df.title = df.apply(
    lambda row : '<a target="_blank" href="{}">{}</a>'.format(
      reverse('viewActivity', args=[row.id]),
      row.title
    ),
    axis=1
  )
  df = df[[
    'timestamp',
    'title',
    'type',
    'distance',
    'time',
    'pace',
    'elevation',
    'averageHr'
  ]]
  
  dfHtml = df.to_html(index=False, escape=False)
  dfHtml = dfHtml[dfHtml.find('<tbody>') : dfHtml.find('</tbody>')] + '</tbody>'
  dfHtml = dfHtml.replace('<tr>0</tr>', '<tr></tr>').replace('NaN', '')
  
  return dfHtml
