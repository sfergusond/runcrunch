from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from app.models import Activity, Athlete

import json

def checkSecretKey(request):
  secretKey = request.META.get('HTTP_SECRETKEY')
  if secretKey != settings.SECRET_KEY:
    return False
  return True

@require_POST
@csrf_exempt
def bulkCreateActivities(request):
  if not checkSecretKey(request):
    return HttpResponse(status=403)
  try:
    data = json.loads(request.body.decode('utf-8'))
    athleteId = int(request.META.get('HTTP_ATHLETE'))
    athlete = Athlete.objects.get(pk=athleteId)
    activities = []
    for i in range(len(data['stravaId'])):
      activity = {k:v[i] for k, v in data.items()}
      activity = Activity(athlete=athlete, **activity)
      activities.append(activity)
    Activity.objects.bulk_create(
      activities,
      batch_size=200,
      unique_fields='stravaId',
      ignore_conflicts=True
    )
    return HttpResponse(status=201)
  except Exception as e:
    print(e)
    return JsonResponse(status=500, data={'Bulk Create Error': str(e)})
