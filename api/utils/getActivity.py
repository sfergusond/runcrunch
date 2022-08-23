import stravalib

def getActivity(athlete, activityId):
  client = stravalib.Client(access_token=athlete.accessToken)
  activity = client.get_activity(activityId)
  return activity
