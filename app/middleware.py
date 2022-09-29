from django.shortcuts import redirect
from django.conf import settings
from .models import Athlete

def athleteMiddleware(get_response):
  def middleware(request):
    if request.user.is_authenticated:
      athlete = Athlete.objects.get(user=request.user)
      request.athlete = athlete
      if athlete.stravaId:
        athlete.stravaReauthenticate()
      # print(athlete.__dict__)
      else:
        redirectUrl = (
          'https://www.strava.com/oauth/authorize?' +
          f'client_id={settings.STRAVA_CLIENT_ID}&' +
          f'redirect_uri={settings.DOMAIN}/connect-to-strava&' +
          'approval_prompt=auto&response_type=code&scope=activity%3Aread%2Cactivity%3Aread_all'
        )
        return redirect(redirectUrl)
    else:
      request.athlete = None
    response = get_response(request)
    return response
  return middleware
