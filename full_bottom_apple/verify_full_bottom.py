"""Checks for the solid bottom-half apple and the untouched source hash."""
import hashlib
import os
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HASH = '8c2ae8b452da705620cd98764d5ecdc385f55724618e09efbd49740f89dc725e'
ok = True


def load(path):
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    return [((struct.unpack('<12fH', d[84+50*i:84+50*i+50])[3:6]),
             (struct.unpack('<12fH', d[84+50*i:84+50*i+50])[6:9]),
             (struct.unpack('<12fH', d[84+50*i:84+50*i+50])[9:12])) for i in range(n)]


def weld(tri, q=1e-4):
    ids, pts = {}, []

    def idx(p):
        k = (round(p[0]/q), round(p[1]/q), round(p[2]/q))
        if k not in ids:
            ids[k] = len(pts)
            pts.append(p)
        return ids[k]

    return pts, [tuple(idx(p) for p in t) for t in tri]


def hits(f, origin, direction):
    out = []
    for a, b, c in f:
        e1 = [b[i]-a[i] for i in range(3)]
        e2 = [c[i]-a[i] for i in range(3)]
        p = [direction[1]*e2[2]-direction[2]*e2[1],
             direction[2]*e2[0]-direction[0]*e2[2],
             direction[0]*e2[1]-direction[1]*e2[0]]
        det = sum(e1[i]*p[i] for i in range(3))
        if abs(det) < 1e-9:
            continue
        s = [origin[i]-a[i] for i in range(3)]
        u = sum(s[i]*p[i] for i in range(3))/det
        if u < -1e-9 or u > 1+1e-9:
            continue
        q = [s[1]*e1[2]-s[2]*e1[1], s[2]*e1[0]-s[0]*e1[2],
             s[0]*e1[1]-s[1]*e1[0]]
        v = sum(direction[i]*q[i] for i in range(3))/det
        if v < -1e-9 or u+v > 1+1e-9:
            continue
        w = sum(e2[i]*q[i] for i in range(3))/det
        if w > 1e-6:
            out.append(w)
    return sorted(out)


tri = load(os.path.join(HERE, 'full_bottom.stl'))
pts, f = weld(tri)
edges = defaultdict(int)
for t in f:
    for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        edges[(min(a, b), max(a, b))] += 1
opens = sum(1 for c in edges.values() if c == 1)
bad = sum(1 for c in edges.values() if c > 2)
par = list(range(len(pts)))


def find(a):
    while par[a] != a:
        par[a] = par[par[a]]
        a = par[a]
    return a


for t in f:
    for b in t[1:]:
        ra, rb = find(t[0]), find(b)
        if ra != rb:
            par[ra] = rb
comps = len({find(i) for i in range(len(pts))})
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
print(f'full_bottom.stl: tris={len(tri)} comps={comps} open={opens} '
      f'nonmanifold={bad} x[{min(xs):.1f},{max(xs):.1f}] '
      f'y[{min(ys):.1f},{max(ys):.1f}] z[{min(zs):.2f},{max(zs):.2f}]')
ok &= comps == 1 and opens == 0 and bad == 0
ok &= abs(min(zs) + 28.94) < 0.4 and abs(max(zs)) < 0.3   # rounded base, flat top at z=0
ok &= max(xs) > 33 and max(ys) > 33                        # full width retained

# sculpted base: dimple at the centre, rounded shoulders out to the apple wall
def bottom_z(r):
    h = hits(tri, (r, 0, -45), (0, 0, 1))
    return -45 + h[0] if h else None

z0, z4, z20, z26 = (bottom_z(r) for r in (0, 4, 20, 26))
profile = [round(v, 2) if v is not None else None for v in (z0, z4, z20, z26)]
print(f'  base profile at r=0,4,20,26: {profile}')
dimple = z0 is not None and z4 is not None and z4 < z0 - 1.0
rounded = z20 is not None and z26 is not None and z20 < z26 - 0.8
print(f'  calyx dimple: {"PASS" if dimple else "FAIL"}   '
      f'rounded base: {"PASS" if rounded else "FAIL"}')
ok &= dimple and rounded

# solid all the way through: ray hits only the base and the flat top
h = sorted({round(-45 + d, 2) for d in hits(tri, (10, 0, -45), (0, 0, 1))})
print(f'  solid through body: {"PASS" if len(h) == 2 else "FAIL"} z={h}')
ok &= len(h) == 2

digest = hashlib.sha256(open(os.path.join(HERE, 'apple_original.stl'), 'rb').read()).hexdigest()
print(f'  apple unchanged: {"PASS" if digest == HASH else "FAIL"}  {digest[:16]}')
ok &= digest == HASH
print('ALL PASS' if ok else 'FAILURES PRESENT')
raise SystemExit(0 if ok else 1)
