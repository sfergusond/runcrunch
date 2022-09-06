import math

COLORS = {
  'background': '#111111',
  'text': 'black',
  'transparent': 'rgba(0,0,0,0)',
  'transparentWhite': 'rgba(255,255,255,.3)',
  'transparentGray': 'rgba(191, 191, 191, .4)',
  'white': 'rgb(255,255,255)',
  'default': '#172b4d',
  'blue': '#5e72e4',
  'whiteT': 'rgba(255,255,255,{})',
  'blueT': 'rgba(94, 114, 228, {})',
  'greenT': 'rgba(45, 206, 137, {})',
  'orangeT': 'rgba(251, 99, 64, {})',
  'orange': '#fb6340',
  'green': '#2dce89',
  'skyBlue': '#11cdef',
  'gray1': '#e9ecef',
  'gray2': '#dee2e6',
  'gray3': '#ced4da',
  'red': '#f5365c',
  'gray': '#e3e2e2',
  'run0': 'rgba(94, 114, 228, {})',
  'run2': 'rgba(45, 206, 137, {})',
  'run1': 'rgba(251, 99, 64, {})',
  'run3': 'rgba(245, 54, 92, {})',
  'run5': 'rgba(23,43,77, {})',
  'run4': 'rgba(207,42,227, {})',
  'run6': 'rgba(36,225,211, {})',
  'Recovery': '#5c5c5c',
  'Endurance - Easy': "#75acff",
  'Endurance - Moderate': "#6de3db",
  'Endurance - Hard': "#3dd44c",
  'Threshold': "#f5e616",
  'Tempo': "#f29624",
  'VO2 Max': "#fa0c0c",
  'Race':'#fc0dec',
  'Race/Anaerobic':'#fc0dec',
  'PR Effort': '#fc0dec',
  '': 'rgba(255,255,255,0)'
}

INTENSITYSCALE = [
   # Recovery
  [0.0, '#5c5c5c'],
  [.3, '#5c5c5c'],
  
  # Easy
  [.3, "#75acff"],
  [.425, "#75acff"],
  
  # Moderate
  [.425, "#6de3db"],
  [.575, "#6de3db"],
  
  # Hard
  [.575, "#3dd44c"],
  [.7, "#3dd44c"],
  
  # Threshold
  [.7, "#f5e616"],
  [.8, "#f5e616"],

  # Tempo
  [.8, "#f29624"],
  [.9, "#f29624"],

  # VO2 max
  [.9, "#fa0c0c"],
  [.95, "#fa0c0c"],

  # Race
  [.95, "#fc0dec"],
  [1.0, '#fc0dec'] 
]
INTENSITYSCALE_SMOOTH = INTENSITYSCALE[::2]
INTENSITYSCALE_SMOOTH.append(INTENSITYSCALE[-1])
INTENSITY_TICK_TEXT = [
  '',
  'Recovery',
  'Endurance<br>(Easy)',
  'Endurance<br>(Moderate)',
  'Endurance<br>(Hard)',
  'Threshold',
  'Tempo',
  'VO2 Max',
  'Race',
]
INTENSITY_BINS = [
  -math.inf,
  0.3,
  0.425,
  0.575,
  0.7,
  0.8,
  0.9,
  0.95,
  1,
  math.inf
]

GRADE_SCALE =  [
  [0,'rgb(0,0,131)'],
  [1/6, 'rgb(0,60,170)'],
  [2/6, 'rgb(5,255,255)'],
  [.5, 'rgb(190,190,190)'],
  [4/6, 'rgb(255,255,0)'],
  [5/6, 'rgb(250,0,0)'],
  [1, 'rgb(128,0,0)']
]
GRADE_SCALE_HIST = [
  'rgb(0,0,131)',
  'rgb(0,60,170)',
  'rgb(5,255,255)',
  'rgb(190,190,190)',
  'rgb(255,255,0)',
  'rgb(250,0,0)',
  'rgb(128,0,0)'
]
