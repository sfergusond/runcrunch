def getPaceMultiplier(grade, elevation):
  altAdjust = 1.75/304.8 # 1.9% VO2 adjust per 1000 ft
  a = -0.00000328132
  b = 0.0014977
  c = 0.0303574
  d = 1
  altitudeAdjustment = (altAdjust * max(elevation - 304.8, 0)) / 100
  if grade == 0:
    gradeAdjustment = 1
  else:
    gradeAdjustment = a * (grade**3) + b * (grade**2) + c * grade + d
  paceMultiplier = gradeAdjustment + altitudeAdjustment
  return paceMultiplier
