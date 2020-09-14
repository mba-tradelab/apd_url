#functions for building a pattern tree
import math
from urllib.parse import urlparse, parse_qs
import logging
from collections import Counter

#decompose a given URL into a processable key-value scheme
def kv_decompose(url):
  pairs = {}
  s = url.split('?', 1)
  for i, v in enumerate(s[0].strip('/').split('/')):
    pairs[i] = v
  if len(s) > 1:
    qs = parse_qs(s[1], keep_blank_values=True)
    qs = {k: ','.join(v) for k, v in qs.items()}
    pairs.update(qs)
  return pairs

#retrieve keywords
def retrieve_keywords(U, S):
  S = {}
  for u in U:
    for k in u.keys():
      s = S.get(k)
      if s is None:
        s = set()
        S[k] = s
      s.add(u.get(k))
  
  V = []
  for s in S.values():
    if len(s) < max(2, min(len(U)) / 5, 10):
      V.extend(s)
  return V

#build pattern tree
def build_tree(U, S, K):
  if len(K) == 0:
    return retrieve_keywords(U, S)
  
  N = len(U)

  H = Counter()
  for k in K:
    C = Counter()
    for u in U:
      C[u.get(k)] += 1
    Hk = 0
    for v, vi in C.items():
      Hk -= float(vi) / N * math.log(float(vi) / N)
    H[k] = Hk
  k_star = H.most_common()[-1][0]

  V = set()
  for u in U:
    v = u.get(k_star)
    if v in S:
      V.add(v)
    else:
      V.add(True)
    
  if len(V) == 1 and True in V:
    return retrieve_keywords(U, S)

  node = []
  K_i = K.copy()
  K_i.remove(k_star)
  for v in V:
    if v == True:
      U_i = [u for u in U if u.get(k_star) not in V]
    else:
      U_i = [u for u in U if u.get(k_star) == v]
    ch = build_tree(U_i, S, K_i)
    node.extend(ch)
  
  return(node)

#process a list of urls
def urls_decomposer(url_list):
  U = [kv_decompose(url) for url in url_list]

  K = Counter()
  for u in U:
    for k in u.keys():
      K[k] += 1
  K = set([k for k, v in K.items() if v > 1])

  V = Counter()
  for u in U:
    for v in u.values():
      V[v] += 1
  V = [v for v in V.most_common() if v[1] > 1]
  pos = 0
  max_decrease = 0
  for i in range(len(V)-1):
    decrease = math.log(V[i][1]) - math.log(V[i+1][1])
    if decrease > max_decrease:
      pos = i
      max_decrease = decrease

  S = set([v[0] for v in V[:pos+1]])
  S.add(None)
  S.update(build_tree(U, S, K))

  return U, K, V, S