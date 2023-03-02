import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

from ..utils.constants import COLORS
from utils.convert import CONVERSIONS, removeNonMovingFromStream, removeUphillFromStream

def skiSpeedZonesGraph(activity, athlete):
  
  unitPref = athlete.unitPreference
  fig = go.Figure()
  
  # Create Distribution
  paceStream = removeNonMovingFromStream(activity['streams']['paceStream'], activity['streams']['movingStream'])
  gradeStream = removeNonMovingFromStream(activity['streams']['gradeStream'], activity['streams']['movingStream'])
  paceStream = removeUphillFromStream(paceStream, gradeStream)
  df = pd.DataFrame(paceStream, columns=['paceStream'])
  df['paceStream'] = list(map(lambda s : round(s), df['paceStream']))
  if unitPref == 'I':
    convertedStream = list(map(
      lambda s : round(CONVERSIONS['metersToMiles'](s) / (CONVERSIONS['secondsToHours'](1))),
      df['paceStream']
    ))
  else:
    convertedStream = list(map(
      lambda s : round(CONVERSIONS['metersToKm'](s) / (CONVERSIONS['secondsToHours'](1))),
      df['paceStream']
    ))
  xVals = np.arange(0, max(convertedStream) + 5, 5)
  df['bins'] = pd.cut(
    convertedStream,
    bins=[-math.inf] + list(xVals),
    labels=[str(i) for i in xVals]
  )
  speedBins = df['bins'].value_counts(normalize=True, sort=False)

  # Create Figure
  hovertext = list(map(
    lambda b : f'{round(b * 100)}%',
    speedBins
  ))
  fig.add_trace(
    go.Bar(
      x=xVals,
      y=speedBins,
      marker=dict(
        color=xVals,
        colorscale='rdylgn_r',
        showscale=False,
        opacity=.85,
        line=dict(
          color=COLORS['blueT'].format('1'),
          width=2
        )
      ),
      hoverinfo='text',
      hovertext=hovertext
    )
  )

  # Update Layout
  ceil = (math.ceil(max(list(speedBins))*10)*10)/100
  ticks = list(np.arange(0, ceil, ceil/10))
  fig.update_layout(
    plot_bgcolor=COLORS['transparent'],
    paper_bgcolor=COLORS['transparent'],
    margin=dict(
      l=0, r=0, t=0, b=0,
      autoexpand=True
    ),
    xaxis=dict(
      ticksuffix=' mph' if unitPref == 'I' else ' km/h',
      tickvals=xVals
    ),
    yaxis=dict(
      tickmode='array',
      tickvals=ticks,
      ticktext=[f'{round(i*100)}%' for i in ticks],
      gridcolor=COLORS['gray'],
      showgrid=True,
      ticks=''
    )
  )

  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    config=dict(displayModeBar=False)
  )

  return figHtml
