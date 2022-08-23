from distutils.command.upload import upload
from django.conf import settings

import boto3
import json
import os

client = boto3.client(
  'lambda',
  region_name=settings.AWS_REGION_NAME,
  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

def callImporter(athlete):
  baseCallbackUrl = os.environ.get('IMPORTER_CALLBACK_URL', settings.DOMAIN) 
  payload = {
    'token': athlete.accessToken,
    'athleteId': athlete.id,
    'uploadEndpoint': baseCallbackUrl + '/api/activity/bulk/create/'
  }
  payload = json.dumps(payload).encode('utf-8')
  client.invoke(
    FunctionName=settings.IMPORTER_SERVICE_FUNCTION_NAME,
    InvocationType='Event',
    Payload=payload
  )
