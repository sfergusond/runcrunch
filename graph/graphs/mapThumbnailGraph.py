from django.conf import settings
import plotly.graph_objects as go
import statistics

from ..utils.constants import COLORS
from ..utils.getBoundsZoomLevel import getBoundsZoomLevel

def mapThumbnail(latStream, lngStream):
  fig = go.Figure()

  # Main Map Trace
  fig.add_trace(
    go.Scattermapbox(
      lat=latStream,
      lon=lngStream,
      mode='lines',
      line=dict(
        color=COLORS['red'],
        width=4
      )
    )
  )

  bounds = [
    max(latStream),
    max(lngStream),
    min(latStream),
    min(lngStream)
  ]
  mapDim = {'height': 170, 'width': 200}

  fig.update_layout(
    height=187,
    width=232,
    margin=dict(
      pad=0,
      l=0,
      r=0,
      t=0,
      b=0,
      autoexpand=False
    ),
    mapbox=dict(
      bearing=0,
      center=go.layout.mapbox.Center(
        lat=statistics.mean(latStream),
        lon=statistics.mean(lngStream)
      ),
      pitch=0,
      zoom=getBoundsZoomLevel(bounds, mapDim)
      ),
    mapbox_style='outdoors',
    mapbox_accesstoken=settings.MAPBOX_TOKEN,
    showlegend=False
  )

  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    full_html=False,
    config=dict(
      displayModeBar=False,
      staticPlot=True
    )
  )
  
  return figHtml
