ALLOWED_ACTIVITY_TYPES = {
  'Run',
  'Walk',
  'Hike',
  'TrailRun',
}

def formatActivity(activity):
  validType = activity.type in ALLOWED_ACTIVITY_TYPES
  formattedActivity = {
    'stravaId': activity.id
  }
  formattedActivity['distance'] = int(round(float(
    activity.distance))) if (activity.distance and validType) else 0
  formattedActivity['elevation'] = int(round(float(
    activity.total_elevation_gain))) if (activity.total_elevation_gain and validType) else None
  formattedActivity['averageHr'] = int(
    activity.average_heartrate) if (activity.average_heartrate and validType) else None
  formattedActivity['timestamp'] = activity.start_date_local.strftime('%Y-%m-%d %H:%M:%S')
  formattedActivity['time'] = activity.moving_time.seconds if (activity.moving_time and validType) else 0
  formattedActivity['title'] = activity.name[:500].replace('\'', ' ').replace('\"', ' ')
  formattedActivity['type'] = activity.type
  return formattedActivity
