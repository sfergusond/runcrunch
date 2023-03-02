import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

from ..utils.constants import COLORS, GRADE_SCALE_HIST
from utils.convert import CONVERSIONS, removeUphillFromStream

def gradeZonesGraph(activity, athlete):
  
  fig = go.Figure()
  
  # Create Distribution
  if not activity['isAmbulatory']:
    activity['streams']['gradeStream'] = list(
      filter(
        lambda x: x < 0, activity['streams']['gradeStream']
      )
    )
  df = pd.DataFrame(activity['streams'], columns=['gradeStream'])
  df['gradeStream'] = list(map(lambda g : round(g), df['gradeStream']))
  xVals = [i for i in range(min(df['gradeStream']), max(df['gradeStream']))]
  df['bins'] = pd.cut(
    df['gradeStream'],
    bins=[-math.inf] + xVals,
    labels=[str(i) for i in xVals]
  )
  gradeBins = df['bins'].value_counts(normalize=True, sort=False)

  # Create Figure
  hoverTemplate = '{:+d}%<br>Freq: {}%<br>{} {}'
  distance = (
    CONVERSIONS['metersToMiles'](activity['fields']['distance']) if athlete.unitPreference == 'I' 
    else CONVERSIONS['metersToKm'](activity['fields']['distance'])
  )
  distanceSuffix = 'mi' if athlete.unitPreference == 'I' else 'km'
  hovertext = list(map(
    lambda x, b : hoverTemplate.format(
      x,
      round(b * 100, 2),
      round(b * distance, 2),
      distanceSuffix
      ),
    xVals, gradeBins
  ))
  fig.add_trace(
    go.Bar(
      x=xVals,
      y=gradeBins,
      marker=dict(
        color=xVals,
        colorscale=GRADE_SCALE_HIST,
        cmid=0,
        cmin=-25,
        cmax=25,
        showscale=False,
        opacity=.85,
        line=dict(
          color=COLORS['blueT'].format('1'),
          width=2
        )
      ),
      width=1,
      hoverinfo='text',
      hovertext=hovertext
    )
  )

  # Update Layout
  ceil = (math.ceil(max(list(gradeBins))*10)*10)/100
  ticks = list(np.arange(0, ceil, ceil/10))
  fig.update_layout(
    plot_bgcolor=COLORS['transparent'],
    paper_bgcolor=COLORS['transparent'],
    margin=dict(
      l=0, r=0, t=0, b=0,
      autoexpand=True
    ),
    xaxis=dict(
      tickformat='+f',
      ticksuffix='%',
      nticks=7
    ),
    yaxis=dict(
      tickmode='array',
      tickvals=ticks,
      ticktext=[f'{int(round(i*100))}%' for i in ticks],
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
