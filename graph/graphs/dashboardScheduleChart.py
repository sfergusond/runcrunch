import datetime
import plotly.figure_factory as ff

from ..utils.getActivityDataFrame import getActivityDataFrame
from ..utils.constants import COLORS

def dashboardScheduleChart(athlete, fromDate, toDate):
  df = getActivityDataFrame(athlete, fromDate, toDate, ['timestamp', 'time'])
  
  baseYr = '2000-01-01 '
  numDays = (toDate - fromDate).days
  xIndex = [(fromDate + datetime.timedelta(days=i)).date() for i in range(numDays)]
  noRunsIndex = list(set(xIndex) - set(df.timestamp.dt.date))
  
  # Build Bars DF
  barsDf = []
  for i, activity in df.iterrows():
    start = baseYr + datetime.datetime.strftime(activity.timestamp, '%H:%M')
    finish = (
      baseYr + 
      datetime.datetime.strftime(
        activity.timestamp + datetime.timedelta(seconds=activity.time),
        '%H:%M'
      )
    )
    bar = {
      'Task': activity.timestamp.date(),
      'Start': start,
      'Finish': finish,
      'Resource': ''
    }
    barsDf.append(bar)
    
  for date in noRunsIndex:
    bar = {
      'Task': date,
      'Start': baseYr + '13:00',
      'Finish': baseYr + '13:00',
      'Resource': ''
    }
    barsDf.append(bar)
    
  barsDf = sorted(barsDf, key=lambda x : x['Task'], reverse=True)
  
  # Create Figure
  fig = ff.create_gantt(
    barsDf,
    showgrid_x=True,
    showgrid_y=True,
    show_hover_fill=False,
    bar_width=.5,
    index_col='Resource',
    group_tasks=True
  )
  
  # Figure layout
  yTickVals = [i for i in range(numDays, -1, -1 * ((numDays // 22) + 1))]
  yTickText = [
    datetime.datetime.strftime(
      toDate - datetime.timedelta(days=i),
      '%a, %m/%d/%y'
    ) for i in yTickVals
  ][::-1]

  fig.update_layout(
    autosize=True,
    paper_bgcolor=COLORS['transparent'],
    plot_bgcolor=COLORS['transparent'],
    margin=dict(
      l=0,r=0,t=0,b=0,
      autoexpand=True
    ),
    xaxis=dict(
      rangeselector=None,
      showspikes=True,
      spikemode='across',
      spikesnap='cursor',
      showgrid=True,
      gridcolor=COLORS['gray'],
      tickformat='%I %p',
      showticksuffix=None,
      hoverformat='%I:%M %p'
    ),
    yaxis=dict(
      type='linear',
      autorange=True,
      spikemode='across',
      spikesnap='data',
      hoverformat='%a %m/%d/%Y',
      tickmode='array',
      tickvals=yTickVals,
      ticktext=yTickText,
      tickformat='%a %m/%d/%Y',
      ticks='outside',
      tickson='boundaries',
      showgrid=True,
      gridcolor=COLORS['transparentGray']
    ),
    hovermode='closest'
  )

  # set hover info
  for i in fig['data']:
    i['hoverinfo'] = 'x+name'
    
  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    full_html=False,
    config=dict(displayModeBar=False)
  )
  
  return figHtml
    