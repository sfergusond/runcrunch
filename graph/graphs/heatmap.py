from django.conf import settings
import plotly.graph_objects as go

from ..utils.constants import COLORS

def heatmap(latStream, lngStream):
  fig = go.Figure()
  if len(latStream) > 250000:
    latStream = latStream[::2]
    lngStream = lngStream[::2]

  heatmap = go.Densitymapbox(
    lat=latStream,
    lon=lngStream,
    zauto=True,
    radius=2.25,
    showlegend=False,
    colorscale='Plasma',
    below=''
  )

  fig.add_trace(heatmap)

  # Update Layout
  fig.update_layout(
    autosize=False,
    width=1400,
    height=690,
    margin=dict(
      pad=0,
      l=0,
      r=0,
      t=0,
      b=0,
      autoexpand=False
    ),
    hovermode=False,
    mapbox=dict(
      bearing=0,
      pitch=0,
      zoom=0
    ),
    mapbox_style='outdoors',
    mapbox_accesstoken=settings.MAPBOX_TOKEN,
    showlegend=False
  )

  # Buttons
  fig.update_layout(
    updatemenus=[
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
              label='<b>Sat + Streets<b>',
              method='relayout'
            )
          ],
        pad=dict(r=0, t=0),
        active=1,
        bordercolor=COLORS['blue'],
        bgcolor=COLORS['gray1'],
        borderwidth=1.5,
        showactive=True,
        x=0.995,
        xanchor='right',
        y=1,
        yanchor='top'
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
