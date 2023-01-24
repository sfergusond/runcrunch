import statistics
import plotly.graph_objects as go

from ..utils.tickInfo import tickInfoStdDev, tickInfoReg
from ..utils.constants import COLORS
from utils.convert import intensityFriendly, speedToPace, speedFriendly 

def lapsBarChart(activity, laps, athlete):
  streams = activity.get('streams')
  unitPref = athlete.unitPreference
  numLaps = len(laps)

  fig = go.Figure()

  # Figure Objects
  hasElev = sum(streams['elevationStream']) > 1
  xIndex = [i for i in range(numLaps)]
  barOffsets = [0] + [
    sum(lap['distance'] for lap in laps[:i]) for i in range(1, numLaps)
  ]
  barWidths = [lap['distance'] for lap in laps]
  if activity['isAmbulatory']:
    paceHoverText = [speedToPace(x['velocity'], unitPref) for x in laps]
    adjPaceHoverText = [speedToPace(x['adjustedPace'], unitPref) for x in laps]
  else:
    paceHoverText = [speedFriendly(x['velocity'], unitPref) for x in laps]
  gapMarker = dict(
    color=COLORS['orangeT'].format('.3'),
    line=dict(
      width=2,
      color=COLORS['orange']
    )
  )
  paceMarker = dict(
    color=COLORS['blueT'].format('.3'),
    line=dict(
      width=2,
      color=COLORS['blue']
    ),
    showscale=False
  )

  fig.add_trace(
    go.Scatter(
      name='Elevation',
      x=streams['distanceStream'],
      y=streams['elevationStream'],
      fill='tozeroy',
      mode='lines',
      line=dict(
        shape='spline',
        smoothing=1,
        color=COLORS['green'],
        simplify=True
      ),
      hoverinfo='skip',
      visible=hasElev
    )
  )
  if activity['isAmbulatory']:
    fig.add_trace(
      go.Bar(
        x=xIndex,
        y=[lap['adjustedPace'] for lap in laps],
        width=barWidths,
        offset=barOffsets,
        opacity=.6,
        hoverinfo='text',
        hovertext=adjPaceHoverText,
        marker=gapMarker,
        visible=False
      )
    )
  fig.add_trace(
    go.Bar(
      x=xIndex,
      y=[lap['velocity'] for lap in laps],
      width=barWidths,
      offset=barOffsets,
      opacity=.6,
      hoverinfo='text',
      hovertext=paceHoverText,
      marker=paceMarker,
      visible=True
    )
  )
  avgPace = statistics.mean(streams['paceStream'])
  paceFriendly = (
    speedToPace(avgPace, unitPref) 
    if activity['isAmbulatory'] 
    else speedFriendly(avgPace, unitPref)
  )
  fig.add_trace(
    go.Scatter(
      name='Avg Pace',
      x=[0, activity['fields']['distance']],
      y=[avgPace] * 2,
      mode='lines',
      line=dict(
        width=1.5,
        shape='linear',
        dash='dash',
        color=COLORS['blue']
      ),
      hoverinfo='name+text',
      hovertext=paceFriendly,
      visible=True
    )
  )
  if activity['isAmbulatory']:
    adjustedPace = statistics.mean(streams['adjustedPaceStream'])
    fig.add_trace(
      go.Scatter(
        name='Avg. Adj. Pace',
        x=[0, activity['fields']['distance']],
        y=[adjustedPace] * 2,
        mode='lines',
        line=dict(
          width=1.5,
          shape='linear',
          dash='dash',
          color=COLORS['orange']
        ),
        hoverinfo='name+text',
        hovertext=speedToPace(adjustedPace, unitPref),
        visible=True
      )
    )

  # Manipulate Axes
  fig['data'][1].update(yaxis='y2')
  fig['data'][2].update(yaxis='y2')
  fig['data'][1].update(xaxis='x2')
  fig['data'][2].update(xaxis='x2')
  if activity['isAmbulatory']:
    fig['data'][3].update(yaxis='y2')
    fig['data'][4].update(yaxis='y2')

  lapTickVals = [
    barOffsets[i] + laps[i]['distance'] / 2 for i in range(numLaps)
  ]
  lapTickText = [str(i + 1) for i in range(numLaps)]
  if activity['isAmbulatory']:
    paceTickVals = tickInfoStdDev(
      [l['velocity'] for l in laps],
      [-4, -2, -2, 0, 2, 4]
    )
    paceTickText = [speedToPace(x, unitPref) for x in paceTickVals]
  else:
    paceTickVals = tickInfoReg(l['velocity'] for l in laps)
    paceTickText = [speedFriendly(x, unitPref) for x in paceTickVals]
  maxElev = max(streams['elevationStream'])
  minElev = min(streams['elevationStream'])
  maxElevGraph = maxElev + ((maxElev - minElev) * .4)
  y2AxisRange = [
    min(streams['paceStream']) * 0.8,
    max(streams['paceStream']) * 1.2
  ]
  if maxElevGraph < 10:
    lpad = 20
  elif maxElevGraph < 1000:
    lpad = 25
  elif maxElevGraph < 10000:
    lpad = 30
  else:
    lpad = 35
  if numLaps >= 10:
    bpad = 25
  else:
    bpad = 15

  fig.update_layout(
    autosize=False,
    showlegend=False,
    plot_bgcolor=COLORS['transparent'],
    margin=dict(
      pad=1,
      l=lpad,
      r=35,
      t=0,
      b=bpad,
      autoexpand=False
    ),
    xaxis=dict(
      showgrid=False,
      visible=False
    ),
    yaxis=dict(
      range=[
        minElev * 0.99,
        maxElevGraph * 1.1
      ],
      side='left',
      showgrid=False,
      visible=False
    ),
    xaxis2=dict(
      showgrid=False,
      overlaying='x',
      tickvals=lapTickVals,
      ticktext=lapTickText,
    ),
    yaxis2=dict(
      range=y2AxisRange,
      showgrid=False,
      overlaying='y',
      side='right',
      anchor='x2',
      position=0,
      visible=True,
      ticks='inside',
      tickvals=paceTickVals,
      ticktext=paceTickText,
    )
  )
  
  # Buttons
  intensityColors = [
    COLORS[intensityFriendly(lap['intensity'])] for lap in laps
  ]
  fig.update_layout(
    updatemenus=[
      dict(
        type='buttons',
        direction='left',
        buttons=[
          dict(
            args=[
              'visible',
              [True, False, True, True, True]
            ],
            args2=[
              'visible',
              [True] * 5
            ],
            label='Toggle GAP',
            method='restyle'
          )
        ],
        pad=dict(r=10, t=10),
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=0.05,
        xanchor='left',
        y=1,
        yanchor='top',
      ),
      dict(
        type='buttons',
        direction='left',
        buttons=[
          dict(
            args=[{
              'marker.color': [
                None,
                COLORS['orangeT'].format('.3'),
                COLORS['blueT'].format('.3')
              ]
            }],
            args2=[{
              'marker.color': [
                None,
                intensityColors,
                intensityColors
              ]
            }],
              label='Toggle Intensity',
              method='restyle'
              )
          ],
        pad=dict(r=10, t=10),
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=.2,
        xanchor="left",
        y=1,
        yanchor="top"
      )
    ]
  )
  
  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    full_html=False,
    config=dict(displayModeBar=False)
  )

  return figHtml