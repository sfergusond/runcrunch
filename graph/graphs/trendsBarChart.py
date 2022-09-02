from turtle import distance
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

from ..utils.constants import COLORS
from ..utils.getActivityDataFrame import getActivityDataFrame
from utils.convert import (
  distanceFriendly,
  elevationFriendly,
  timeFriendly,
  heartrateFriendly,
  speedToPace
)

def yearToColor(year, alpha):
  yrHash = hash(year)
  r = (yrHash & 0xFF0000) >> 16
  g = (yrHash & 0x00FF00) >> 8
  b = (yrHash & 0x0000FF)
  color = f'rgba({r},{g},{b},{alpha})'
  return color

def getHoverText(series, metric, unitPref):
  if metric == 'distance':
    hovertext = [distanceFriendly(x, unitPref) for x in series[metric]]
  elif metric == 'time':
    hovertext = [timeFriendly(x) for x in series[metric]]
  elif metric == 'pace':
    hovertext = [speedToPace(x, unitPref) for x in series[metric]]
  elif metric == 'elevation':
    hovertext = [elevationFriendly(x, unitPref) for x in series[metric]]
  elif metric == 'averageHr':
    hovertext = [heartrateFriendly(x) for x in series[metric]]
  else:
    hovertext = ''
  return hovertext

def trendsBarChart(athlete, metric, period):
  unitPref = athlete.unitPreference
  fig = go.Figure()
  if metric == 'pace':
    df = getActivityDataFrame(
      athlete,
      datetime.datetime.min,
      datetime.datetime.max - datetime.timedelta(days=1),
      ['timestamp', 'distance', 'time']
    )
    df['pace'] = df['distance'] / df['time']
  else:
    df = getActivityDataFrame(
      athlete,
      datetime.datetime.min,
      datetime.datetime.max - datetime.timedelta(days=1),
      ['timestamp', metric]
    )
  byPeriodDf = df.groupby(
    by=df.timestamp.dt.strftime(
      '%Y-%W' if period == 'weekly' else '%Y-%m'
    )
  )
  metricDf = byPeriodDf.agg({
    'timestamp': 'min',
    metric: 'mean' if metric in ('averageHr', 'pace') else 'sum'
  })
  metricDf['period'] = metricDf.timestamp.dt.strftime(
    '%W' if period == 'weekly' else '%m'
  )
  metricDf['year'] = metricDf.timestamp.dt.strftime('%Y')
  metricDf.set_index(['year', 'period'], inplace=True)
  years = metricDf.index.levels[0]
  xIndex = metricDf.index.levels[1]
  if period == 'weekly':
    xIndex = [int(x) - 1 for x in xIndex]
  else:
    xIndex = [datetime.datetime.strptime(x, '%m').strftime('%b') for x in xIndex]
  numYears = len(years)
  colorsLine = [yearToColor(y, 1) for y in years]
  colorsBar = [yearToColor(y, 0.3) for y in years]
  
  for i, year in enumerate(years):
    series = metricDf.loc[year]
    hovertext = getHoverText(series, metric, unitPref)
    fig.add_trace(
      go.Bar(
        name=f'<b>{year}</b>',
        x=xIndex,
        y=series[metric],
        width=1,
        visible=True if i == numYears - 1 else 'legendonly',
        marker=dict(
          line=dict(
            width=2,
            color=colorsLine[i]
          ),
          color=colorsBar[i]
        ),
        text=hovertext,
        textposition='inside',
        hoverinfo='name+text',
        hovertext=hovertext,
        showlegend=True
      )
    )
    
  fig.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    hovermode='x',
    margin=dict(
      l=0,r=0,t=0,b=25,
      autoexpand=True,
    ),
    barmode='overlay',
    showlegend=True,
    legend=dict(
      itemclick='toggle',
      itemdoubleclick='toggleothers',
      xanchor='right',
      yanchor='top',
      bgcolor=COLORS['transparent']
    ),
    yaxis=dict(
      visible=False,
      fixedrange=True
    ),
    xaxis=dict(
      title=dict(
        text='Week' if period =='weekly' else ''
      ),
      fixedrange=True
    )
  )

  # Buttons
  fig.update_layout(
    updatemenus=[
      dict(
        direction='down',
        buttons=[
          dict(
            args=[
              {
                'width': [1] * numYears,
                'stackgroup': [''] * numYears,
                'fill': ['tozeroy'] * numYears
              },
              {
                'barmode': 'overlay',
                'yaxis.autorange': False,
                'yaxis.ticks': 'outside',
                'yaxis.showticklabels': True,
                'yaxis.showgrid': True
              },
            ],
            label='<b>Overlay</b>',
            method='update'
          ),
          dict(
            args=[
              {
                'width': [1 / (numYears * 2)] * numYears,
                'stackgroup': [''] * numYears,
                'fill': ['tozeroy'] * numYears
              },
              {
                'barmode': 'group',
                'yaxis.autorange': False,
                'yaxis.ticks': 'outside',
                'yaxis.showticklabels': True,
                'yaxis.showgrid': True
              }
            ],
            label='<b>Group</b>',
            method='update'
          ),
          dict(
            args=[
              {
                'width': [1] * numYears,
                'stackgroup': ['one'] * numYears,
                'fill': ['tonexty'] * numYears
              },
              {
                'barmode': 'stack',
                'yaxis.autorange': True,
                'yaxis.ticks': '',
                'yaxis.showticklabels': False,
                'yaxis.showgrid': False
              }
            ],
            label='<b>Stack</b>',
            method='update'
          )
        ],
        pad=dict(r=0, t=0),
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=0,
        xanchor='left',
        y=1,
        yanchor='top',
        active=0
      )
    ]
  )
    
  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    config=dict(displayModeBar=False)
  )
  
  return figHtml
