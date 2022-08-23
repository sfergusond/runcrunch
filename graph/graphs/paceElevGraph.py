import plotly.graph_objects as go
import math

from ..utils.constants import COLORS
from ..utils.tickInfo import tickInfo
from ..utils.hoverInfo import getElevationHoverInfo, getPaceHoverInfo, getHrHoverInfo
from utils.convert import convertStream

def paceElevGraph(
  distanceStream,
  paceStream, 
  adjustedPaceStream, 
  elevationStream, 
  hrStream,
  athlete
  ):
  unitPref = athlete.unitPreference
  fig = go.Figure()
  
  distanceStream = convertStream(
    distanceStream,
    'metersToMiles' if unitPref == 'I' else 'metersToKm'
  )
  
  paceHoverInfo = getPaceHoverInfo(paceStream, unitPref)
  paceTickInfo = tickInfo(paceStream)
  fig.add_trace(
    go.Scatter(
      name='Pace',
      x=distanceStream,
      y=paceStream,
      yaxis='y2',
      mode='lines',
      opacity=0.65,
      line=dict(
        width=2,
        shape='spline',
        smoothing=1.1,
        color=COLORS['blue'],
        simplify=True
      ),
      hoverinfo='x+text',
      hovertext=paceHoverInfo
    )
  )
  
  if sum(elevationStream) > 1:
    if unitPref == 'I':
      elevationStream = convertStream(elevationStream, 'metersToFeet')
    elevationHoverInfo = getElevationHoverInfo(elevationStream, unitPref)
    fig.add_trace(
      go.Scatter(
        name='Elevation',
        x=distanceStream,
        y=elevationStream,
        fill='tozeroy',
        mode='lines',
        yaxis='y',
        line=dict(
          shape='spline',
          smoothing=1,
          color=COLORS['green'],
          simplify=True,
        ),
        fillcolor=COLORS['greenT'].format('.3'),
        hoverinfo='x+text',
        hovertext=elevationHoverInfo
      )
    )
  
  if sum(adjustedPaceStream) > 0:
    adjustedPaceHoverInfo = getPaceHoverInfo(adjustedPaceStream, unitPref)
    adjustedPaceTickInfo = tickInfo(adjustedPaceStream)
    fig.add_trace(
      go.Scatter(
        name='Adj. Pace',
        x=distanceStream,
        y=adjustedPaceStream,
        yaxis='y2',
        mode='lines',
        opacity=0.65,
        fill='tonexty',
        line=dict(
          width=2,
          shape='spline',
          smoothing=1.1,
          color=COLORS['orange'],
          simplify=True
        ),
        hoverinfo='x+text',
        hovertext=adjustedPaceHoverInfo
      )
    )
  else:
    adjustedPaceTickInfo = [None, -1, math.inf, None]

  if sum(hrStream) > 0:
    hrHoverInfo = getHrHoverInfo(hrStream)
    fig.add_trace(
      go.Scatter(
        name='HR',
        x=distanceStream,
        y=hrStream,
        yaxis='y3',
        mode='lines',
        opacity=0.65,
        line=dict(
          width=2,
          shape='spline',
          smoothing=1.1,
          color=COLORS['red'],
          simplify=True
        ),
        hoverinfo='x+text',
        hovertext=hrHoverInfo,
        visible=True
      )
    )

  # Axis Settings
  maxElev = max(elevationStream)
  minElev = min(elevationStream)
  rangePace = [
    min(paceTickInfo[1], adjustedPaceTickInfo[1]),
    max(paceTickInfo[-2], adjustedPaceTickInfo[-2])
  ]

  fig.update_layout(
    xaxis=dict(
      domain=[0,1],
      zeroline=False,
      showgrid=False,
      ticks='inside',
      ticksuffix=' mi' if unitPref == 'I' else ' km',
      showticksuffix='all',
      tickcolor=COLORS['text'],
      hoverformat='.2r',
    ),
    # Elevation
    yaxis=dict(
      domain=[0,1],
      range=[minElev - 10, maxElev * 1.01],
      side='right',
      zeroline=False,
      showgrid=False,
      ticks='outside',
      ticksuffix='ft' if unitPref == 'I' else 'm',
      showticksuffix='first',
      tickcolor=COLORS['text'],
    ),
    # Pace
    yaxis2=dict(
      domain=[0,1],
      range=rangePace,
      side='left',
      zeroline=False,
      overlaying='y',
      gridwidth=1,
      gridcolor=COLORS['blue'],
      showgrid=False,
      tickvals=paceTickInfo,
      ticktext=getPaceHoverInfo(paceTickInfo, unitPref),
      ticks='outside',
      tickcolor=COLORS['text'],
      visible=True
    ),
    yaxis3=dict(
      domain=[0,1],
      autorange=True,
      side='right',
      zeroline=False,
      overlaying='y',
      gridwidth=1,
      gridcolor=COLORS['red'],
      showgrid=False,
      ticks='outside',
      ticksuffix='bpm',
      showticksuffix='last',
      tickcolor=COLORS['text'],
      visible=False
    )
  )

  # Aesthetic Settings
  if maxElev < 10:
      rpad = 55
  elif maxElev < 1000:
      rpad = 60
  elif maxElev < 10000:
      rpad = 65
  else:
      rpad = 70

  fig.update_layout(
    plot_bgcolor=COLORS['transparent'],
    paper_bgcolor=COLORS['transparent'],
    width=1110,
    height=450,
    margin=dict(
      pad=0,
      l=175,
      r=rpad,
      t=0,
      b=15,
      autoexpand=False
    ),
    font=dict(
      color=COLORS['text']
    ),
    hovermode='x unified',
    hoverlabel=dict(
      bgcolor=COLORS['whiteT'].format('.75'),
      namelength=0
    ),
    showlegend=True,
    legend=dict(
      itemclick='toggle',
      itemdoubleclick='toggleothers',
      x=-.2,
      xanchor='left',
      y=1,
      yanchor='top'
    )
  )
  
  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    full_html=False,
    config={'displayModeBar': False}
  )
  
  return figHtml
