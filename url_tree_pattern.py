# -*-coding: utf-8 -*-

import math
from urllib.parse import urlparse
import logging
from collections import Counter

class URLNormalizer:
    def __init__(self):
        self.logger = logging.getLogger(URLNormalizer.__name__)

    def fit(self, urls):
        U = [self._to_key_value_pair(url) for url in urls]

        K = Counter()
        for u in U:
            for k in u.keys():
                K[k] += 1
        self.K = set([k for k, v in K.items() if v > 1])
        self.logger.debug('K = %s', self.K)

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
        S.update(self._build(U, S, self.K))
        self.logger.debug('salient values: %s', S)
        self.S = S

        return self

    def _to_key_value_pair(self, url):
        pairs = {}
        e = url.split('?', 1)
        for i, v in enumerate(e[0].strip('/').split('/')):
            pairs[i] = v
        if len(e) > 1:
            qs = urlparse.parse_qs(e[1], keep_blank_values=1)
            qs = {k:','.join(v) for k, v in qs.items()}
            pairs.update(qs)
        return pairs

    def _build(self, U, S, K):
        if len(K) == 0:
            return self._retrieve_keywords(U,  S)

        N = len(U)

        H = Counter()
        for k in K:
            C = Counter()
            for u in U:
                C[u.get(k)] += 1
            Hk = 0
            for v, vi in C.items():
                ratio = float(vi) / N
                Hk += - ratio * math.log(ratio)
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
            return self._retrieve_keywords(U, S)

        node = []
        K_i = K.copy()
        K_i.remove(k_star)
        for v in V:
            if v == True:
                U_i = [u for u in U if u.get(k_star) not in V]
            else:
                U_i = [u for u in U if u.get(k_star) == v]
            ch = self._build(U_i, S, K_i)
            node.extend(ch)

        return node

    def _retrieve_keywords(self, U, S):
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
            if len(s) < max(2, min(len(U) / 5, 10)):
                V.extend(s)

        return V

    def transform(self, url):
        K, V = self.K, self.S
        u = {k: v for k, v in self._to_key_value_pair(url).items() if k in K}
        i = 0
        path = []
        while True:
            s = u.get(i)
            if s is None:
                break
            path.append(s if s in V else '*')
            i = i + 1
        qs = []
        for k in sorted(u.keys()):
            if type(k) != int:
                if k not in K:
                    continue
                v = u.get(k, '')
                if v in V:
                    qs.append('%s=%s' % (k, v))
                else:
                    qs.append('%s=*' % k)

        return '/%s?%s' % ('/'.join(path), '&'.join(qs))

if __name__ == '__main__':
    import sys
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)
    f = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
    lines = [line.strip() for line in f.readlines()]
    model = URLNormalizer().fit(lines)
    for line in lines:
        print(model.transform(line), line)