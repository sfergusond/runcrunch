import math

from utils.convert import CONVERSIONS

# Lorentz constants by percentile
# See: https://www.sciencedirect.com/science/article/abs/pii/S0143622818307859

TABLE = [
  (0.01,-2.100,12.273,21.816,0.263,-0.00193),
  (0.05,-1.527,14.041,36.813,0.320,-0.00273),
  (0.10,-1.568,13.328,38.892,0.404,-0.00323),
  (0.15,-1.626,11.847,38.231,0.481,-0.00356),
  (0.20,-1.710,10.154,36.905,0.557,-0.00389),
  (0.25,-1.822,8.827,37.111,0.616,-0.00402),
  (0.30,-1.858,8.412,39.995,0.645,-0.00430),
  (0.35,-1.891,8.584,44.852,0.649,-0.00443),
  (0.40,-1.958,8.960,50.340,0.649,-0.00457),
  (0.45,-2.050,9.402,56.172,0.646,-0.00460),
  (0.50,-2.171,10.064,63.660,0.628,-0.00463),
  (0.55,-2.317,10.712,71.572,0.608,-0.00451),
  (0.60,-2.459,11.311,79.287,0.599,-0.00461),
  (0.65,-2.647,12.089,89.143,0.576,-0.00465),
  (0.70,-2.823,12.784,98.697,0.566,-0.00493),
  (0.75,-3.067,13.888,113.655,0.518,-0.00488),
  (0.80,-3.371,15.395,134.409,0.443,-0.00472),
  (0.85,-3.661,17.137,159.027,0.385,-0.00534),
  (0.90,-3.060,16.653,138.875,0.823,-0.01386),
  (0.95,-3.485,17.033,138.040,1.179,-0.0125),
  (0.99,-4.000,13.903,123.515,1.961,-0.01081)
]

def _grade_to_angle(grade):
  return math.atan(grade/100) * 100

def model(theta, A, B, C, D, E):
    return C * (1 / ((math.pi * B) * (1 + ((theta - A) / B) ** 2))) + D + E * theta  
  
def adjustedVelocity(grade, velocity):
  theta = _grade_to_angle(grade)
  
  rows = []

  for p, A, B, C, D, E in TABLE:
      v_theta = model(theta, A, B, C, D, E)
      v_zero = model(0, A, B, C, D, E)
      rows.append((p, v_theta, v_zero))

  rows.sort(key=lambda x: x[1])

  for i in range(len(rows) - 1):

    _, v1, z1 = rows[i]
    _, v2, z2 = rows[i+1]

    if v1 <= velocity <= v2 or v2 <= velocity <= v1:
      t = (velocity - v1) / (v2 - v1)
      v0_interp = z1 + t * (z2 - z1)

      return v0_interp

  # fallback if outside range
  closest = min(rows, key=lambda x: abs(x[1] - velocity))
  return closest[2]


def getAltitudeMultiplier(elevation): 
  # If under 3000ft, no adjustment
  if CONVERSIONS["metersToFeet"](elevation) < 3000:
    return 1
  
  # About 2% adjust per 1000 ft above 3000 ft
  altAdjust = 1 + (0.02 * ((CONVERSIONS["metersToFeet"](elevation) - 3000) / 1000))
  return altAdjust  
