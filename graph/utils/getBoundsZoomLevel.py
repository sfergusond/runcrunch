import numpy as np

def getBoundsZoomLevel(bounds, mapDim):
  # https://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
  
  ne_lat = bounds[0]
  ne_long = bounds[1]
  sw_lat = bounds[2]
  sw_long = bounds[3]

  scale = 2 # adjustment to reflect MapBox base tiles are 512x512 vs. Google's 256x256
  WORLD_DIM = {'height': 256 * scale, 'width': 256 * scale}
  ZOOM_MAX = 18

  def latRad(lat):
      sin = np.sin(lat * np.pi / 180)
      radX2 = np.log((1 + sin) / (1 - sin)) / 2
      return max(min(radX2, np.pi), -np.pi) / 2

  def zoom(mapPx, worldPx, fraction):
      return np.floor(np.log(mapPx / worldPx / fraction) / np.log(2))

  latFraction = (latRad(ne_lat) - latRad(sw_lat)) / np.pi

  lngDiff = ne_long - sw_long
  lngFraction = ((lngDiff + 360) if lngDiff < 0 else lngDiff) / 360

  latZoom = zoom(mapDim['height'], WORLD_DIM['height'], latFraction)
  lngZoom = zoom(mapDim['width'], WORLD_DIM['width'], lngFraction)

  return min(latZoom, lngZoom, ZOOM_MAX)
