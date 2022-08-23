import statistics

SPACE_LIST = [-5, -3, -2, -1, 0, 1, 2, 3, 5]

def tickInfo(series, space_list=SPACE_LIST):
  mean = statistics.mean(series)
  stdev = statistics.stdev(series)
  ticks = [mean + (i * stdev) for i in space_list]
  return ticks

def getIntensityTicks(easyPace, prPace):
  ticks = [
    easyPace, # min
    .5875 * prPace, # easy .65
    .68125 * prPace, # moderate .7125
    .75 * prPace, # hard .7875
    .81875 * prPace, # thresh .85
    .875 * prPace, # tempo .9
    .925 * prPace, # vo2 .95
    .9625 * prPace, # race .975
    .9875 * prPace  # max 1
  ]
  return ticks
