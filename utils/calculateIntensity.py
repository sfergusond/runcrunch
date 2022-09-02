def calculateIntensity(athlete, speed, distance):
  if not athlete.prDistance or not athlete.prTime:
    return None
  if distance == 0:
    return 0
  easyPace = 2.06 # 13 min/mile
  speed = speed - easyPace
  prSpeed = athlete.prDistance / athlete.prTime
  prEffort = (
    prSpeed * (
      (athlete.prDistance / distance) ** 0.07
      )
    ) - easyPace
  intensity = round((speed/prEffort) * 100, 2)
  return intensity
