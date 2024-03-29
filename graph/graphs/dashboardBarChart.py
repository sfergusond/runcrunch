import pandas as pd
import plotly.graph_objects as go
import datetime
from django.shortcuts import reverse

from ..utils.constants import COLORS
from ..utils.getActivityDataFrame import getActivityDataFrame
from utils.convert import (
  timeFriendly,
  distanceFriendly,
  elevationFriendly
)

def getActivityMatrix(df, maxStacks):
  matrix = [ [ 0 ] * len(df.index) for i in range(maxStacks) ] 
  for i, (date, val) in enumerate(df.iteritems()):
    for j, v in enumerate(val):
      if not pd.isna(v):
        matrix[j][i] = int(v)
      else:
        matrix[j][i] = 0
  return matrix

def getWeeklySpans(fromDate, toDate):
  numDays = (toDate - fromDate).days + 1
  linePoints = [1 if i % 7 == 0 else 0 for i in range(numDays)]
  linePointsIndex = [
    fromDate + datetime.timedelta(days=i - 1, hours=12) for i in range(numDays)
  ]
  
  # Shift by index of first Monday
  mondayIndex = 0
  tmpDay = fromDate
  while tmpDay.weekday() != 0:
    tmpDay += datetime.timedelta(days=1)
    mondayIndex += 1
  linePoints = [0] * mondayIndex + linePoints
  
  return linePoints, linePointsIndex

def getWeeklySpanTickInfo(df, athlete, metric):
  unitPref = athlete.unitPreference
  dfByWeek = df.groupby(by=df.timestamp.dt.strftime('%Y-%W')).sum()
  if metric == 'distance':
    tickInfo = list(map(
      lambda x : f'<b>{distanceFriendly(x, unitPref)}</b>', dfByWeek['distance']
    ))
  elif metric == 'time':
    tickInfo = list(map(
      lambda x : f'<b>{timeFriendly(x)}</b>', dfByWeek['time']
    ))
  elif metric == 'elevation':
    tickInfo = list(map(
      lambda x : f'<b>{elevationFriendly(x, unitPref)}</b>', dfByWeek['elevation']
    ))
  return tickInfo

def getWeeklySpanTickPoints(df):
  tickPoints = []
  dfByWeek = df.groupby(by=df.timestamp.dt.strftime('%Y-%W')).size()
  for week in dfByWeek.index:
    point = datetime.datetime.strptime(week + '-4', '%Y-%W-%w')
    tickPoints.append(point)
  return tickPoints

def getMetricAnnotation(val, metric, unitPref):
  if metric == 'distance':
    return distanceFriendly(val, unitPref)
  elif metric == 'time':
    return timeFriendly(val)
  elif metric == 'elevation':
    return elevationFriendly(val, unitPref)
  return

def getBarAnnotations(matrix, unitPref, metric, xIndex):
  barTotals = list(map(sum, zip(*matrix)))
  maxY = max(barTotals)
  bump = (25 if len(xIndex) < 30 else 80) * (maxY / 1000)
  angle = 0 if len(xIndex) < 30 else 90
  if metric == 'distance':
    getText = lambda x : f'<b>{distanceFriendly(x, unitPref)}</b>'
  elif metric == 'time':
    getText = lambda x : f'<b>{timeFriendly(x)}</b>'
  elif metric == 'elevation':
    getText = lambda x : f'<b>{elevationFriendly(x, unitPref)}</b>'
  annotations = [{
    'x': x,
    'y': y + bump,
    'yref': 'y2',
    'text': getText(y),
    'showarrow': False,
    'textangle': angle,
  } for x, y in zip(xIndex, barTotals)]
  return annotations

def dashboardBarChart(athlete, metric, fromDate, toDate):
  unitPref = athlete.unitPreference
  df = getActivityDataFrame(athlete, fromDate, toDate, ['timestamp', 'id', metric])
  byDate = df.groupby(by=df.timestamp.dt.date)
  dfByDate = byDate.agg({metric: lambda x : list(x)})[metric]
  maxStacks = byDate.size().max()
  xIndex = list(dfByDate.index)
  matrix = getActivityMatrix(dfByDate, maxStacks)
    
  # Create Figure
  fig = go.Figure()
  
  for i, level in enumerate(matrix):
    colors = list(map(
      lambda v, c : c.format('1') if v else COLORS['transparent'], 
      level,
      [COLORS[f'run{i % 4}']] * len(xIndex),
    ))
    hovertext = [getMetricAnnotation(y, metric, unitPref) for y in level]
    fig.add_trace(
      go.Bar(
        name=f'Run {i + 1}',
        x=xIndex,
        y=level,
        xaxis='x2',
        yaxis='y2',
        hovertext=hovertext,
        hoverinfo='x+text',
        marker=dict(
          line=dict(
            width=2,
            color=colors,
          ),
          color=COLORS[f'run{i % 4}'].format('.3')
        ),
        visible=True
      )
    )
    
  # Create weekly spans
  linePoints, linePointsIndex = getWeeklySpans(fromDate, toDate)
  fig.add_trace(
    go.Bar(
      x=linePointsIndex,
      y=linePoints,
      xaxis='x',
      yaxis='y',
      visible=True,
      width=1,
      opacity=0.5,
      marker=dict(
        line=dict(
          width=2,
          color='black'
        )
      )
    )
  )
    
  # Update layout
  tickPoints = getWeeklySpanTickPoints(df)
  weeklyTickInfo = getWeeklySpanTickInfo(df, athlete, metric)
  barAnnotations = getBarAnnotations(matrix, athlete.unitPreference, metric, xIndex)
  fig.update_layout(
    paper_bgcolor=COLORS['transparent'],
    plot_bgcolor=COLORS['transparent'],
    margin=dict(
      l=0,r=0,t=0,b=0,
      autoexpand=True
    ),
    uniformtext=dict(
      minsize=1,
      mode='show'
    ),
    barmode='stack',
    bargap=0.1,
    hovermode='closest',
    showlegend=False,
    annotations=barAnnotations,
    yaxis2=dict(
      fixedrange=True,
      visible=False,
      overlaying='y',
      showgrid=False,
      domain=[0,1],
    ),
    xaxis2=dict(
      type='date',
      overlaying='x',
      tickvals=xIndex,
      automargin=True,
      fixedrange=True,
      zeroline=False,
      tickformat='%a, %b %d'
    ),
    yaxis=dict(
      type='linear',
      range=[0,1],
      fixedrange=True,
      visible=False,
      showgrid=False,
    ),
    xaxis=dict(
      type='date',
      fixedrange=True,
      matches='x2',
      side='top',
      showgrid=False,
      zeroline=False,
      visible=True,
      automargin=True,
      # position text at midpoint of each week
      tickmode='array',
      tickvals=tickPoints,
      ticktext=weeklyTickInfo
    ),
  )
  
  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    config=dict(displayModeBar=False)
  )
  
  return figHtml