from django.conf import settings

import boto3

RAW_MAP = {
  8:r'\b',
  7:r'\a',
  12:r'\f',
  10:r'\n',
  13:r'\r',
  9:r'\t',
  11:r'\v'
}

client = boto3.client(
  's3',
  region_name=settings.AWS_REGION_NAME,
  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

def updatePolyline(activity, athlete):
  if not activity.map.summary_polyline:
    print('No Polyline')
    return
  key = f'polyline-{athlete.id}.txt'
  existingPolyline = getOrCreatePolyline(key)
  newPolyline = r''.join(
    i if ord(i) > 32 else RAW_MAP.get(ord(i), i) for i in activity.map.summary_polyline
    )
  polyline = existingPolyline + newPolyline + r','
  uploadPolyline(polyline, key)
  
def getOrCreatePolyline(key):
  try:
    obj = client.get_object(
      Bucket=settings.AWS_POLYLINE_BUCKET_NAME,
      Key=key
    )
    polyline = obj['Body'].read().decode('utf-8')
    return polyline
  except:
    return ''
  
def uploadPolyline(polyline, key):
  body = polyline.encode('utf-8')
  client.put_object(
    Bucket=settings.AWS_POLYLINE_BUCKET_NAME,
    Key=key,
    Body=body
  )
