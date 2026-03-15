import numpy as np

from utils.convert import CONVERSIONS

# Lorentz constants by percentile
# See: https://www.sciencedirect.com/science/article/abs/pii/S0143622818307859

P = np.array([
  0.01,0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,
  0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,0.99
])

A = np.array([
  -2.100,-1.527,-1.568,-1.626,-1.710,-1.822,-1.858,-1.891,-1.958,-2.050,
  -2.171,-2.317,-2.459,-2.647,-2.823,-3.067,-3.371,-3.661,-3.060,-3.485,-4.000
])

B = np.array([
  12.273,14.041,13.328,11.847,10.154,8.827,8.412,8.584,8.960,9.402,
  10.064,10.712,11.311,12.089,12.784,13.888,15.395,17.137,16.653,17.033,13.903
])

C = np.array([
  21.816,36.813,38.892,38.231,36.905,37.111,39.995,44.852,50.340,56.172,
  63.660,71.572,79.287,89.143,98.697,113.655,134.409,159.027,138.875,138.040,123.515
])

D = np.array([
  0.263,0.320,0.404,0.481,0.557,0.616,0.645,0.649,0.649,0.646,
  0.628,0.608,0.599,0.576,0.566,0.518,0.443,0.385,0.823,1.179,1.961
])

E = np.array([
  -0.00193,-0.00273,-0.00323,-0.00356,-0.00389,-0.00402,-0.00430,-0.00443,
  -0.00457,-0.00460,-0.00463,-0.00451,-0.00461,-0.00465,-0.00493,-0.00488,
  -0.00472,-0.00534,-0.01386,-0.0125,-0.01081
])


def model(theta, A, B, C, D, E):
    return C * (1 / ((np.pi * B) * (1 + ((theta - A) / B) ** 2))) + D + E * theta

def interp_extrap(x, xp, fp):
  """Linear interpolation with linear extrapolation."""
  if x <= xp[0]:
    slope = (fp[1] - fp[0]) / (xp[1] - xp[0])
    return fp[0] + slope * (x - xp[0])
  elif x >= xp[-1]:
    slope = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
    return fp[-1] + slope * (x - xp[-1])
  else:
    return np.interp(x, xp, fp)


def adjustedVelocity(theta, velocity):
  v_theta = model(theta, A, B, C, D, E)

  order = np.argsort(v_theta)
  v = v_theta[order]
  p = P[order]

  if velocity <= v[0]:
    slope = (p[1] - p[0]) / (v[1] - v[0])
    p_est = p[0] + slope * (velocity - v[0])
  elif velocity >= v[-1]:
    slope = (p[-1] - p[-2]) / (v[-1] - v[-2])
    p_est = p[-1] + slope * (velocity - v[-1])
  else:
    idx = np.searchsorted(v, velocity)
    v1, v2 = v[idx-1], v[idx]
    p1, p2 = p[idx-1], p[idx]
    t = (velocity - v1) / (v2 - v1)
    p_est = p1 + t * (p2 - p1)

  A_i = interp_extrap(p_est, P, A)
  B_i = interp_extrap(p_est, P, B)
  C_i = interp_extrap(p_est, P, C)
  D_i = interp_extrap(p_est, P, D)
  E_i = interp_extrap(p_est, P, E)

  return model(0.0, A_i, B_i, C_i, D_i, E_i)

  v_theta = model(theta, A, B, C, D, E)

  order = np.argsort(v_theta)
  v = v_theta[order]
  p = P[order]

  if velocity <= v[0]:
    # extrapolate below range
    slope = (p[1] - p[0]) / (v[1] - v[0])
    p_est = p[0] + slope * (velocity - v[0])

  elif velocity >= v[-1]:
    # extrapolate above range
    slope = (p[-1] - p[-2]) / (v[-1] - v[-2])
    p_est = p[-1] + slope * (velocity - v[-1])

  else:
    # interpolation inside range
    idx = np.searchsorted(v, velocity)
    v1, v2 = v[idx-1], v[idx]
    p1, p2 = p[idx-1], p[idx]

    t = (velocity - v1) / (v2 - v1)
    p_est = p1 + t * (p2 - p1)

  # interpolate coefficients at percentile
  A_i = np.interp(p_est, P, A)
  B_i = np.interp(p_est, P, B)
  C_i = np.interp(p_est, P, C)
  D_i = np.interp(p_est, P, D)
  E_i = np.interp(p_est, P, E)

  return model(0.0, A_i, B_i, C_i, D_i, E_i)


def getAltitudeMultiplier(elevation): 
  # If under 3000ft, no adjustment
  if CONVERSIONS["metersToFeet"](elevation) < 3000:
    return 1
  
  # About 2% adjust per 1000 ft above 3000 ft
  altAdjust = 1 + (0.02 * ((CONVERSIONS["metersToFeet"](elevation) - 3000) / 1000))
  return altAdjust  
