import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from ..utils.constants import INTENSITY_BINS
from utils.convert import speedToPace, timeFriendly, distanceFriendly

LABELS = [
  'recovery',
  'easy',
  'moderate',
  'hard',
  'threshold',
  'tempo',
  'vo2',
  'race',
  'pr'
]
LEAVES_LABELS = [
  'Recovery',
  'Endurance', 'Easy', 'Moderate', 'Hard',
  'Workout', 'Threshold', 'Tempo', 'VO2 Max',
  'Race', 'Race', 'PR Effort'
]
LEAVES_IDS = [
  'Recovery',
  'Endurance', 'Easy', 'Moderate', 'Hard',
  'Workout', 'Threshold', 'Tempo', 'VO2 Max',
  'Race', 'Race/Anaerobic', 'PR Effort'
]
SECTOR_COLORS = colors = [
  'rgb(255,255,255)',
  '#5c5c5c',
  '#3ed6d6', "#75acff", "#6de3db", "#3dd44c",
  '#e8b417', "#f5e616", "#f29624", "#fa0c0c",
  '#fc0dec', '#fc0dec', '#fc0dec'
]

def getPaceCounts(paceStream, bins):
  df = pd.DataFrame(paceStream, columns=['pace'])
  df['paceZones'] = pd.cut(df.pace, bins=bins, labels=LABELS)
  counts = df.paceZones.value_counts(normalize=True, sort=False)
  return counts

def getDistributionVars(counts):
  distValues = [
    # Base
    counts.sum(),
    # Recovery parent/leaf
    counts['recovery'],
    # Endurance parent
    counts['easy'] + counts['moderate'] + counts['hard'],
    # Endurance leaves
    counts['easy'], counts['moderate'], counts['hard'],
    # Workout parent
    counts['threshold'] + counts['tempo'] + counts['vo2'],
    # Workout leaves
    counts['threshold'], counts['tempo'], counts['vo2'],
    # Race parent
    counts['race'] + counts['pr'],
    # Race leaves
    counts['race'], counts['pr']
  ]
  return distValues

def getHoverText(activity, counts, paceRanges, unitPref):
  pctPace = [int(round(float(p) * 100)) for p in counts]
  tmPace = [int(round(float(p) * float(activity['fields']['time']))) for p in counts]
  distPace = [int(round(float(p) * float(activity['fields']['distance']))) for p in counts]
  zippedPace = list(map(
    lambda pz, p, t, d : f'{pz}<br><b>{p}%<br>{timeFriendly(t)}<br>{distanceFriendly(d, unitPref)}</b>',
    paceRanges, pctPace, tmPace, distPace
  ))

  hovertext = [
    '',
    zippedPace[0],
    f'''
    <b>{pctPace[1] + pctPace[2] + pctPace[3]}%<br>
    {timeFriendly(tmPace[1] + tmPace[2] + tmPace[3])}<br>
    {distanceFriendly(distPace[1] + distPace[2] + distPace[3], unitPref)}</b>
    ''',
    zippedPace[1], zippedPace[2], zippedPace[3],
    f'''
    <b>{pctPace[4] + pctPace[5] + pctPace[6]}%<br>
    {timeFriendly(tmPace[4] + tmPace[5] + tmPace[6])}<br>
    {distanceFriendly(distPace[4] + distPace[5] + distPace[6], unitPref)}</b>
    ''',
    zippedPace[4], zippedPace[5], zippedPace[6],
    f'''
    <b>{pctPace[7] + pctPace[8]}%<br>
    {timeFriendly(tmPace[7] + tmPace[8])}<br>
    {distanceFriendly(distPace[7] + distPace[8], unitPref)}</b>
    ''',
    zippedPace[7], zippedPace[8]
  ]
  return hovertext

def paceZonesGraph(activity, athlete):
  unitPref = athlete.unitPreference
  streams = activity['streams']

  # Data Crunch
  easyPace = athlete.getEasyPace()
  prPace = athlete.getRelativePrPace(activity['fields']['distance']) - easyPace

  paceStream = [p - easyPace for p in streams['paceStream']]
  adjPaceStream = None
  if streams.get('adjustedPaceStream'):
    adjPaceStream = [p - easyPace for p in streams['adjustedPaceStream']]

  # Distribution vars
  bins = [i * prPace for i in INTENSITY_BINS]

  # Make dataframes and cut into bins
  paceCounts = getPaceCounts(paceStream, bins)
  if adjPaceStream:
    adjPaceCounts = getPaceCounts(adjPaceStream, bins)
    
  # Distribution values
  distValuesPace = getDistributionVars(paceCounts)
  if adjPaceStream:
    distValuesAdjPace = getDistributionVars(adjPaceCounts)

  paceRanges = (
    [speedToPace(bins[1] + easyPace, unitPref)] +
    [(
      speedToPace(bins[i] + easyPace, unitPref) +
      ' - ' +
      speedToPace(bins[i - 1] + easyPace, unitPref)
    ) for i in range(2, 9)
    ] +
    [speedToPace(bins[-2] + easyPace, unitPref)] 
  )
  
  # Hovertext
  paceHovertext = getHoverText(activity, paceCounts, paceRanges, unitPref)
  if adjPaceStream:
    adjPaceHovertext = getHoverText(activity, adjPaceCounts, paceRanges, unitPref)
  
  # Create Figure
  fig = go.Figure()
  fig = make_subplots(1, 2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
  
  base = '<b>Pace Zones</b>'
  fig.add_trace(
    go.Sunburst(
      name='Pace Zones',
      ids=[base] + LEAVES_IDS,
      labels=[base] + LEAVES_LABELS,
      parents=[
        '',
        base,
        base, 'Endurance', 'Endurance', 'Endurance',
        base, 'Workout', 'Workout', 'Workout',
        base, 'Race', 'Race'
      ],
      values=distValuesPace,
      marker=dict(
        colors=colors,
        line=dict(width=1.5)
      ),
      leaf=dict(
        opacity=1
      ),
      branchvalues='total',
      hovertext=paceHovertext,
      hoverinfo='label+text',
      insidetextorientation='auto',
      domain=dict(column=0)
    ),
    1, 1
  )

  if adjPaceStream:
    base = '<b>GAP Zones</b>'
    fig.add_trace(
      go.Sunburst(
        name='Pace Zones',
        ids=[base] + LEAVES_IDS,
        labels=[base] + LEAVES_LABELS,
        parents=[
          '',
          base,
          base, 'Endurance', 'Endurance', 'Endurance',
          base, 'Workout', 'Workout', 'Workout',
          base, 'Race', 'Race'
        ],
        values=distValuesAdjPace,
        marker=dict(
          colors=colors,
          line=dict(width=1.5)
        ),
        leaf=dict(
          opacity=1
        ),
        branchvalues='total',
        hovertext=adjPaceHovertext,
        hoverinfo='label+text',
        insidetextorientation='auto',
        domain=dict(column=0)
      ),
      1, 2
    )
    
  # Update Layout
  fig.update_layout(
    margin=dict(t=0, l=0, r=0, b=15)
  )

  figHtml = fig.to_html(
    include_plotlyjs=False,
    include_mathjax=False,
    full_html=False,
    config=dict(displayModeBar=False)
  )
  
  return figHtml
