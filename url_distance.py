def levenshtein_distance2(s1, s2):
  l1, l2 = len(s1), len(s2)

  if s1 == s2:
    return np.float64(0)
  elif l1 == 0:
    return np.float64(l2)
  elif l2 == 0:
    return np.float64(l1)
  
  v0 = np.array([None]*(l2+1))
  v1 = np.array([None]*(l2+1))
  for i in range(len(v0)):
    v0[i] = i
  for i in range(l1):
    v1[0] = i+1
    for j in range(l2):
      if s1[i] == s2[j]:
        C = np.float64(0)
      else:
        C = np.float64(2)
      v1[j+1] = min(v1[j]+1, v0[j+1]+1, v0[j]+C)
    for j in range(len(v0)):
      v0[j] = v1[j]

  return v1[l2]

def url_distance(s1, s2):
  l1, l2 = len(s1), len(s2)

  if s1 == s2:
    return np.float64(0)
  elif l1 == 0:
    return np.float64(l2)
  elif l2 == 0:
    return np.float64(l1)

  return np.float64(1 - (l1+l2-levenshtein_distance2(s1, s2))/(l1+l2))