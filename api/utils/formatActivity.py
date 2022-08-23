def formatActivity(activity):
  formattedActivity = {
    'stravaId': activity.id
  }
  formattedActivity['distance'] = int(round(float(
    activity.distance))) if activity.distance else None
  formattedActivity['elevation'] = int(round(float(
    activity.total_elevation_gain))) if activity.total_elevation_gain else None
  formattedActivity['averageHr'] = int(
    activity.average_heartrate) if activity.average_heartrate else None
  formattedActivity['timestamp'] = activity.start_date_local.strftime('%Y-%m-%d %H:%M:%S')
  if activity.start_latlng:
    formattedActivity['startLat'] = float(activity.start_latlng[0])
    formattedActivity['startLng'] = float(activity.start_latlng[1])
  else:
    formattedActivity['startLat'] = None
    formattedActivity['startLng'] = None
  formattedActivity['time'] = activity.moving_time.seconds if activity.moving_time else 0
  formattedActivity['title'] = activity.name[:500].replace('\'', ' ').replace('\"', ' ')
  return formattedActivity
