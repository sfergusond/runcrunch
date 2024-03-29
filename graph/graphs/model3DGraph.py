import plotly.graph_objects as go

from ..utils.constants import INTENSITYSCALE, INTENSITY_TICK_TEXT, GRADE_SCALE, COLORS, SPEED_SCALE
from ..utils.tickInfo import getIntensityTicks
from ..utils.hoverInfo import (
  getDistanceHoverInfo, 
  getElevationHoverInfo, 
  getGradeHoverInfo, 
  getPaceHoverInfo,
  getSpeedHoverInfo
)
from utils.convert import convertStream

def model3DGraph(activity, athlete):
  fig = go.Figure()
  unitPref = athlete.unitPreference  
  
  # Pace Zone Colorbar
  relativePr = athlete.getRelativePrPace(activity['fields']['distance'])
  easyPace = athlete.getEasyPace()
  if activity['isAmbulatory']:
    paceZones = dict(
      width=10,
      color=activity['streams']['paceStream'],
      cmin=easyPace,
      cmax=relativePr,
      showscale=True,
      colorscale=INTENSITYSCALE,
      colorbar=dict(
        thickness=20,
        x=0,
        y=0,
        yanchor='bottom',
        len=0.7,
        tickfont=dict(size=8),
        tickangle=0,
        tickmode='array',
        tickvals=getIntensityTicks(easyPace, relativePr),
        ticktext=INTENSITY_TICK_TEXT
      )
    )

    adjustedPaceZones = dict(
      width=10,
      color=activity['streams']['adjustedPaceStream'],
      cmin=easyPace,
      cmax=relativePr,
      showscale=True,
      colorscale=INTENSITYSCALE,
      colorbar=dict(
        thickness=20,
        x=0,
        y=0,
        yanchor='bottom',
        len=0.7,
        tickfont=dict(size=8),
        tickangle=0,
        tickmode='array',
        tickvals=getIntensityTicks(easyPace, relativePr),
        ticktext=INTENSITY_TICK_TEXT
      )
    )
  else:
    paceZones = dict(
      width=10,
      color=activity['streams']['paceStream'],
      cmin=min(activity['streams']['paceStream']),
      cmax=max(activity['streams']['paceStream']),
      showscale=True,
      colorscale=SPEED_SCALE
    )
    adjustedPaceZones = paceZones

  maxGrade = max(activity['streams']['gradeStream'])
  minGrade = min(activity['streams']['gradeStream'])
  gradeZones = dict(
    width=10,
    color=activity['streams']['gradeStream'],
    cmax=max(10, max(maxGrade, abs(minGrade))),
    cmin=min(-10, min(minGrade, -1 * maxGrade)),
    cmid=0,
    showscale=True,
    colorscale=GRADE_SCALE,
    reversescale=False,
    colorbar=dict(
      thickness=20,
      x=0,
      y=0,
      yanchor='bottom',
      len=0.7,
      tickfont=dict(size=8),
      tickangle=0,
    )
  )

  defaultLine = dict(
    width=10,
    color=COLORS['red']
  )

  # Create figure objects
  elevationStream = activity['streams']['elevationStream']
  if unitPref == 'I':
    elevationStream = convertStream(elevationStream, 'metersToFeet')
  distanceStream = convertStream(
    activity['streams']['distanceStream'], 
    'metersToMiles' if unitPref == 'I' else 'metersToKm'
  )
  distanceHoverInfo = getDistanceHoverInfo(distanceStream, unitPref)
  elevationHoverInfo = getElevationHoverInfo(elevationStream, unitPref)
  gradeHoverInfo = getGradeHoverInfo(activity['streams']['gradeStream'])
  if activity['isAmbulatory']:
    paceHoverInfo = getPaceHoverInfo(activity['streams']['paceStream'], unitPref)
    adjPaceHoverInfo = getPaceHoverInfo(activity['streams']['adjustedPaceStream'], unitPref)
  else:
    paceHoverInfo = getSpeedHoverInfo(activity['streams']['paceStream'], unitPref)
    adjPaceHoverInfo = [''] * len(activity['streams']['adjustedPaceStream'])
  hoverTemplate = 'Dist: {}<br>Pace: {}<br>Adj. Pace: {}<br>Elev: {}<br>Grade: {}'
  hoverInfo = list(map(
    lambda d, p, ap, e, g : hoverTemplate.format(d, p, ap, e, g),
    distanceHoverInfo,
    paceHoverInfo,
    adjPaceHoverInfo,
    elevationHoverInfo,
    gradeHoverInfo
  ))
  fig.add_trace(
    go.Scatter3d(
      y=activity['streams']['latStream'],
      x=activity['streams']['lngStream'],
      z=elevationStream,
      mode='lines',
      line=defaultLine,
      hoverinfo='text',
      hovertext=hoverInfo,
      projection=dict(
        y=dict(show=True),
        x=dict(show=True)
      ),
      surfacecolor=COLORS['transparentGray']
    )
  )

  # Update Layout
  maxElev = max(elevationStream)
  minElev = min(elevationStream)
  maxLat = max(activity['streams']['latStream'])
  minLat = min(activity['streams']['latStream'])
  maxLng = max(activity['streams']['lngStream'])
  minLng = min(activity['streams']['lngStream'])
  if maxElev - minElev > 200:
      maxZ = maxElev + 100
  elif maxElev - minElev > 50:
      maxZ = maxElev + 25
  else:
      maxZ = maxElev + (maxElev - minElev) * 5
  if minElev < 0:
      minZ = minElev
  elif minElev < 100:
      minZ = 0
  else:
      minZ = minElev - 100
  fig.update_layout(
    autosize=True,
    margin=dict(
      pad=0,
      l=0,
      r=0,
      t=0,
      b=0,
      autoexpand=False,
    ),
    scene_camera=dict(
      eye=dict(
        x=3,
        y=3,
        z=0.1
      )
    ),
    scene=dict(
      xaxis=dict(
        title='',
        visible=True,
        backgroundcolor=COLORS['transparent'],
        showgrid=False,
        showticklabels=False,
        ticks='',
        mirror=True
      ),
      yaxis=dict(
        title='',
        visible=True,
        backgroundcolor=COLORS['transparent'],
        showgrid=False,
        showticklabels=False,
        ticks='',
        mirror=True
      ),
      zaxis=dict(
        range=[minZ, maxZ],
        backgroundcolor=COLORS['transparent'],
        title="<b>Elevation</b>",
        showgrid=True,
        gridcolor='black',
        gridwidth=.5,
        ticks='',
        ticksuffix='ft' if unitPref == 'I' else 'm',
        showticksuffix='last',
        mirror=True
      )
    ),
    scene_aspectmode='manual',
    scene_aspectratio=dict(
      x=100 * (maxLng - minLng),
      y=125 * (maxLat - minLat),
      z=1
    )
  )

  # Add Buttons
  fig.update_layout(
    updatemenus=[
      dict(
        type='buttons',
        direction='left',
        buttons=[
          dict(
            args2=['line', paceZones],
            args=['line', defaultLine],
            label='<b>Toggle Pace Zones</b>',
            method='restyle'
          )
        ],
        visible=True,
        pad=dict(r=10, t=1),
        bgcolor=COLORS['gray1'],
        bordercolor=COLORS['blue'],
        borderwidth=1.5,
        showactive=True,
        x=0,
        xanchor="left",
        y=0.92,
        yanchor="bottom"
      ), 
      dict(
        type='buttons',
        direction='left',
        buttons=[
          dict(
            args2=['line', gradeZones],
            args=['line', defaultLine],
            label='<b>Toggle Grades</b>',
            method='restyle'
          )
        ],
        pad=dict(r=10, t=1),
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=0,
        xanchor="left",
        y=0.72,
        yanchor="bottom"
      ), 
      dict(
        type='buttons',
        direction='left',
        buttons=[
          dict(
            args2=['line', adjustedPaceZones],
            args=['line', defaultLine],
            label='<b>Toggle Adj. Pace Zones</b>',
            method='restyle'
          )
        ],
        pad=dict(r=10, t=1),
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=0,
        xanchor="left",
        y=0.82,
        yanchor="bottom"
      )
    ]
  )
  
  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    full_html=False,
    config={'displayModeBar': False}
  )

  return figHtml
