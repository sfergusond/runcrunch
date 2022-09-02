import statistics
import plotly.graph_objects as go

from django.conf import settings
from ..utils.constants import COLORS
from ..utils.getLaps import getAutoLaps
from ..utils.getBoundsZoomLevel import getBoundsZoomLevel
from utils.convert import elevationFriendly

def annotatedMap(athlete, activity):
  unitPref = athlete.unitPreference
  streams = activity['streams']

  fig = go.Figure()

  # Main Map Trace
  fig.add_trace(
    go.Scattermapbox(
      lat=streams['latStream'],
      lon=streams['lngStream'],
      mode='lines',
      line=dict(
        color=COLORS['red'],
        width=4
      )
    )
  )

  # Auto Laps - INDEX 1
  autoLapIndices = getAutoLaps(activity, athlete, retIndices=True)
  autoLapsLat = [streams['latStream'][i] for i in autoLapIndices]
  autoLapsLng = [streams['lngStream'][i] for i in autoLapIndices]

  fig.add_trace(
    go.Scattermapbox(
      lat=autoLapsLat,
      lon=autoLapsLng,
      mode='markers+text',
      text=[f'{i+1}' for i in range(len(autoLapIndices))],
      textposition='top right',
      hoverinfo='text',
      marker=dict(
        symbol='circle',
        size=6,
        color='black'
      )
    )
  )

  # Device Laps - INDEX 2
  deviceLapIndices = list(map(lambda x: x['startIndex'], activity['laps']))[1:]
  deviceLapsLat = [streams['latStream'][i] for i in deviceLapIndices]
  deviceLapsLng = [streams['lngStream'][i] for i in deviceLapIndices]

  try:
    fig.add_trace(
      go.Scattermapbox(
        lat=deviceLapsLat,
        lon=deviceLapsLng,
        mode='markers+text',
        text=[f'Lap {i + 1}' for i in range(len(deviceLapIndices))],
        textposition='top right',
        hoverinfo='text',
        opacity=1,
        marker=dict(
          symbol='circle',
          size=6,
          color=COLORS['Recovery']
        )
      )
    )
  except:
    fig.add_trace(
      go.Scattermapbox(
      lat=autoLapsLat,
      lon=autoLapsLng,
      mode='none',
      visible=False
    )
  )


  # Highest/Lowest points INDEX 3, 4
  if streams.get('elevationStream'):
    minElev, maxElev = min(streams['elevationStream']), max(streams['elevationStream'])
    elevHigh = streams['elevationStream'].index(maxElev)
    elevLow = streams['elevationStream'].index(minElev)
    elevHighLat = [streams['latStream'][elevHigh]]
    elevHighLng = [streams['lngStream'][elevHigh]]
    elevLowLat = [streams['latStream'][elevLow]]
    elevLowLng = [streams['lngStream'][elevLow]]
    markerTextHigh = elevationFriendly(maxElev, unitPref)
    markerTextLow = elevationFriendly(minElev, unitPref)

    fig.add_trace(
      go.Scattermapbox(
        lat=elevHighLat,
        lon=elevHighLng,
        opacity=1,
        mode='markers+text',
        text=f'Highest Point<br>{markerTextHigh}',
        textposition='top right',
        hoverinfo='text',
        marker=dict(
          opacity=1,
          symbol='circle',
          size=6,
          color=COLORS['green']
        )
      )
    )
    fig.add_trace(
      go.Scattermapbox(
        lat=elevLowLat,
        lon=elevLowLng,
        opacity=1,
        mode='markers+text',
        text=f'Lowest Point<br>{markerTextLow}',
        textposition='top right',
        hoverinfo='text',
        hoverlabel=dict(
          bgcolor='rgba(255,255,255,.75)',
          bordercolor=COLORS['red'],
        ),
        marker=dict(
          opacity=1,
          symbol='circle',
          size=6,
          color=COLORS['gray']
        )
      )
    )

  # Update Layout
  bounds = [
    max(streams['latStream']),
    max(streams['lngStream']),
    min(streams['latStream']),
    min(streams['lngStream'])
  ]
  mapDim = {'height': 600, 'width': 1200}

  fig.update_layout(
    height=mapDim['height'],
    margin=dict(
      pad=0,
      l=0, r=0, t=0, b=0,
      autoexpand=False
    ),
    hovermode='closest',
    mapbox=dict(
      bearing=0,
      center=go.layout.mapbox.Center(
        lat=statistics.mean(streams['latStream']),
        lon=statistics.mean(streams['lngStream'])
      ),
      pitch=0,
      zoom=getBoundsZoomLevel(bounds, mapDim)
      ),
    mapbox_style='outdoors',
    mapbox_accesstoken=settings.MAPBOX_TOKEN,
    showlegend=False
  )

  # Add Buttons
  fig.update_layout(
    updatemenus=[
      dict(
        direction='down',
        buttons=[
          dict(
            args=[
              'visible',
              [True] + [False] * 6
            ],
            label='<b>None</b>',
            method='restyle'
            ),
          dict(
            args=[
              'visible',
              [True, True] + [False] * 5
            ],
            label='<b>Auto Splits</b>',
            method='restyle'
          ),
          dict(
            args=[
              'visible',
              [True, False, True] + [False] * 4
            ],
            label='<b>Device Splits</b>',
            method='restyle'
          ),
          dict(
            args=[
              'visible',
              [True] + [False] * 2 + [True] * 4
              ],
              label='<b>Min/Max</b>',
              method='restyle'
          ),
          dict(
            args=[
              'visible',
              [True] * 7
            ],
            label='<b>All</b>',
            method='restyle'
          )
        ],
        active=4,
        pad=dict(r=0, t=0),
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=0.875,
        xanchor="right",
        y=0.9975,
        yanchor="top"
      ), 
      dict(
        direction='down',
        buttons=[
          dict(
            args=['mapbox.style', 'streets'],
            label='<b>Basic</b>',
            method='relayout'
          ),
          dict(
            args=['mapbox.style', 'outdoors'],
            label='<b>Topographic</b>',
            method='relayout'
          ),
          dict(
            args=['mapbox.style', 'satellite'],
            label='<b>Satellite</b>',
            method='relayout'
          ),
          dict(
            args=['mapbox.style', 'satellite-streets'],
            label='<b>Sat + Streets</b>',
            method='relayout'
          )
        ],
        pad=dict(r=10, t=1),
        active=1,
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=1,
        xanchor='right',
        y=1,
        yanchor='top'
      )
    ]
  )
  
  figHtml = fig.to_html(
    include_mathjax=False,
    include_plotlyjs=False,
    full_html=False,
    config=dict(displayModeBar=False)
  )
  
  return figHtml
