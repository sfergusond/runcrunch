from django.conf import settings

import boto3
import itertools
import six
import math
import codecs
import psutil

RAW_MAP = {
  8:r'\b',
  7:r'\a',
  12:r'\f',
  10:r'\n',
  13:r'\r',
  9:r'\t',
  11:r'\v'
}

class PolylineCodec(object):
  def _pcitr(self, iterable):
    return six.moves.zip(iterable, itertools.islice(iterable, 1, None))

  def _py2_round(self, x):
    # The polyline algorithm uses Python 2's way of rounding
    return int(math.copysign(math.floor(math.fabs(x) + 0.5), x))

  def _write(self, output, curr_value, prev_value, factor):
    curr_value = self._py2_round(curr_value * factor)
    prev_value = self._py2_round(prev_value * factor)
    coord = curr_value - prev_value
    coord <<= 1
    coord = coord if coord >= 0 else ~coord

    while coord >= 0x20:
      output.write(six.unichr((0x20 | (coord & 0x1f)) + 63))
      coord >>= 5

    output.write(six.unichr(coord + 63))

  def _trans(self, value, index):
    byte, result, shift = None, 0, 0

    while byte is None or byte >= 0x20:
      byte = ord(value[index]) - 63
      index += 1
      result |= (byte & 0x1f) << shift
      shift += 5
      comp = result & 1

    return ~(result >> 1) if comp else (result >> 1), index

  def decode(self, expression, precision=5, geojson=False):
    coordinates, index, lat, lng, length, factor = [], 0, 0, 0, len(expression), float(10 ** precision)

    while index < length:
      lat_change, index = self._trans(expression, index)
      lng_change, index = self._trans(expression, index)
      lat += lat_change
      lng += lng_change
      coordinates.append((lat / factor, lng / factor))

    if geojson is True:
      coordinates = [t[::-1] for t in coordinates]

    return coordinates

  def encode(self, coordinates, precision=5, geojson=False):
    if geojson is True:
      coordinates = [t[::-1] for t in coordinates]

    output, factor = six.StringIO(), int(10 ** precision)

    self._write(output, coordinates[0][0], 0, factor)
    self._write(output, coordinates[0][1], 0, factor)

    for prev, curr in self._pcitr(coordinates):
      self._write(output, curr[0], prev[0], factor)
      self._write(output, curr[1], prev[1], factor)

    return output.getvalue()
  
def decode(expression, precision=6, geojson=False):
  """
  Decode a polyline string into a set of coordinates.
  :param expression: Polyline string, e.g. 'u{~vFvyys@fS]'.
  :param precision: Precision of the encoded coordinates. Google Maps uses 5, OpenStreetMap uses 6.
      The default value is 5.
  :param geojson: Set output of tuples to (lon, lat), as per https://tools.ietf.org/html/rfc7946#section-3.1.1
  :return: List of coordinate tuples in (lat, lon) order, unless geojson is set to True.
  """
  return PolylineCodec().decode(expression, precision, geojson)


def encode(coordinates, precision=6, geojson=False):
  """
  Encode a set of coordinates in a polyline string.
  :param coordinates: List of coordinate tuples, e.g. [(0, 0), (1, 0)]. Unless geojson is set to True, the order
      is expected to be (lat, lon).
  :param precision: Precision of the coordinates to encode. Google Maps uses 5, OpenStreetMap uses 6.
      The default value is 5.
  :param geojson: Set to True in order to encode (lon, lat) tuples.
  :return: The encoded polyline string.
  """
  return PolylineCodec().encode(coordinates, precision, geojson)

def getStreamsFromPolyline(athlete):  
  print('RAM Used (GB) getStreams (start):', psutil.virtual_memory()[3]/1000000000)
  polyline = ''
  client = boto3.client(
    's3',
    region_name=settings.AWS_REGION_NAME,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
  )
  key = f'polyline-{athlete.id}.txt'
  try:
    body = client.get_object(
      Bucket=settings.AWS_POLYLINE_BUCKET_NAME,
      Key=key
    )['Body'] #.read().decode('utf-8')
    print('RAM Used (GB) getStreams (get body):', psutil.virtual_memory()[3]/1000000000)
  except Exception as e:
    print(e)
    raise e
  
  for chunk in codecs.getreader('utf-8')(body):
    polyline += chunk
  print('RAM Used (GB) getStreams (after chunks):', psutil.virtual_memory()[3]/1000000000)
  
  latStream, lngStream = [], []
  polylineTraces = polyline.split(',')
  for trace in polylineTraces:
    raw = r''.join(
      i if ord(i) > 32 else RAW_MAP.get(ord(i), i) for i in trace
    )
    decoded = decode(raw, precision=5)
    if decoded:
      latStream += list(map(lambda x : x[0], decoded))
      lngStream += list(map(lambda x : x[1], decoded))
      
  print('RAM Used (GB) getStreams (before return):', psutil.virtual_memory()[3]/1000000000)
  
  return latStream, lngStream
