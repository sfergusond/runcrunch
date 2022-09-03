from django.urls import reverse
from django.conf import settings

import boto3
import json

client = boto3.client(
  'lambda',
  region_name=settings.AWS_REGION_NAME,
  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

def callImporter(request):
  if settings.DEBUG:
    uploadEndpoint = settings.DOMAIN + reverse('bulkActivityCreate')
  else:
    uploadEndpoint = request.build_absolute_uri(
      reverse('bulkActivityCreate')
    ).replace('http:', 'https:')
  payload = {
    'token': request.athlete.accessToken,
    'athleteId': request.athlete.id,
    'uploadEndpoint': uploadEndpoint
  }
  print('Importer Payload:', payload)
  payload = json.dumps(payload).encode('utf-8')
  client.invoke(
    FunctionName=settings.IMPORTER_SERVICE_FUNCTION_NAME,
    InvocationType='Event',
    Payload=payload
  )
