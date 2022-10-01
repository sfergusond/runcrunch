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
      request.athlete = None
    response = get_response(request)
    return response
  return middleware
