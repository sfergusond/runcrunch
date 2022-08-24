import calendar
import datetime

def getNextSunday(startDay=None):
  if not startDay:
    startDay = datetime.datetime.today()
  daysAhead = 6 - startDay.weekday()
  if daysAhead <= 0:
    return startDay
  nextSunday = startDay + datetime.timedelta(daysAhead)
  return nextSunday
    