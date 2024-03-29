from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.utils import IntegrityError

import json

from .utils.getActivity import getActivity
from .utils.formatActivity import formatActivity
from .utils.updatePolyline import updatePolyline, deletePolyline
from app.models import Athlete, Activity

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def eventReceiver(request):
  try:
    if request.method == 'POST':
      body = json.loads(request.body)
      aspectType = body['aspect_type']
      objectType = body['object_type']
      print('Received Event:', body)
      
      if objectType == 'activity':
        
        if aspectType == 'create':
          athlete = Athlete.objects.get(stravaId=body['owner_id'])
          print('Webhook Athlete:', athlete.__dict__)
          athlete.stravaReauthenticate()
          stravaActivity = getActivity(athlete, body['object_id'])
          try:
            formattedActivity = formatActivity(stravaActivity)
            activity = Activity.objects.create(athlete=athlete, **formattedActivity)
            activity.save()
            updatePolyline(stravaActivity, athlete)
          except IntegrityError:
            return HttpResponse(status=200)
          except Exception as e:
            print('Activity Create Error:', e)
            return HttpResponse(status=500)
            
        elif aspectType == 'update':
          Activity.objects.filter(
            stravaId=body['object_id']
          ).update(**body['updates'])
        
        elif aspectType == 'delete':
          try:
            activity = Activity.objects.get(stravaId=body['object_id'])
            activity.delete()
          except:
            return HttpResponse(status=200)
        
      elif (objectType == 'athlete' 
            and aspectType == 'update'
            and body['updates']['authorized'] == 'false'):
        pass
      return HttpResponse(status=200)
    
    elif request.method == 'GET':
      # Handle webhook subscription creation
      challenge = dict(request.GET.items())['hub.challenge']
      return JsonResponse({'hub.challenge': challenge}, status=200)
    
  except Exception as e:
    print(e)
    return HttpResponse(status=500)
  
  return HttpResponse(status=404)
