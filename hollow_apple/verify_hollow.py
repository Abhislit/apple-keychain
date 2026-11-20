"""STL checks for the hollow apple plus an unchanged-source hash check."""
import hashlib
import math
import os
import struct
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HASH = '8c2ae8b452da705620cd98764d5ecdc385f55724618e09efbd49740f89dc725e'


def load(path):
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    return [((struct.unpack('<12fH', d[84+50*i:84+50*i+50])[3:6]),
             (struct.unpack('<12fH', d[84+50*i:84+50*i+50])[6:9]),
             (struct.unpack('<12fH', d[84+50*i:84+50*i+50])[9:12])) for i in range(n)]


BED_Z0 = {'shell': -20.0, 'cap': -25.938, 'stem_leaf': 20.2}


def shift(tri, dz):
    """Undo bed alignment so the assembly-coordinate geometry checks still work."""
    return [tuple((p[0], p[1], p[2] + dz) for p in t) for t in tri]


def weld(tri, q=1e-4):
    ids, pts = {}, []

    def idx(p):
        k = (round(p[0]/q), round(p[1]/q), round(p[2]/q))
        if k not in ids:
            ids[k] = len(pts)
            pts.append(p)
        return ids[k]

    return pts, [tuple(idx(p) for p in t) for t in tri]


def report(name, tri):
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
    print(f'{name}: tris={len(tri)} comps={comps} open={opens} nonmanifold={bad} '
          f'x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}] '
          f'z[{min(zs):.1f},{max(zs):.1f}]')
    ok = comps == 1 and opens == 0 and bad == 0
    return pts, f, ok


def hits(pts, f, o, d):
    out = []
    for t in f:
        a, b, c = (pts[i] for i in t)
        e1 = [b[i]-a[i] for i in range(3)]
        e2 = [c[i]-a[i] for i in range(3)]
        p = [d[1]*e2[2]-d[2]*e2[1], d[2]*e2[0]-d[0]*e2[2], d[0]*e2[1]-d[1]*e2[0]]
        det = sum(e1[i]*p[i] for i in range(3))
        if abs(det) < 1e-9:
            continue
        s = [o[i]-a[i] for i in range(3)]
        u = sum(s[i]*p[i] for i in range(3))/det
        if u < -1e-9 or u > 1+1e-9:
            continue
        q = [s[1]*e1[2]-s[2]*e1[1], s[2]*e1[0]-s[0]*e1[2], s[0]*e1[1]-s[1]*e1[0]]
        v = sum(d[i]*q[i] for i in range(3))/det
        if v < -1e-9 or u+v > 1+1e-9:
            continue
        w = sum(e2[i]*q[i] for i in range(3))/det
        if w > 1e-6:
            out.append(w)
    return sorted({round(x, 3) for x in out})


def ray(pts, f, label, o, d, ok_fn):
    h = hits(pts, f, o, d)
    ok = bool(ok_fn(h))
    print(f'  {label}: {"PASS" if ok else "FAIL"} dist={[round(x,2) for x in h[:4]]}')
    return ok


ps, fs, ok = report('shell.stl', shift(load(os.path.join(HERE, 'shell.stl')),
                                       BED_Z0['shell']))
pc, fc, okc = report('cap.stl', shift(load(os.path.join(HERE, 'cap.stl')),
                                      BED_Z0['cap']))
ok &= okc
pa, fa, oka = report('apple_complete_hollow.stl',
                     load(os.path.join(HERE, 'apple_complete_hollow.stl')))
ok &= oka

print('--- stem / leaf split ---')
body_top = max(p[2] for p in pa)
shell_top = max(p[2] for p in ps)
no_stem = body_top < 28 and shell_top < 28
print(f'  apple body top z={body_top:.2f}, shell top z={shell_top:.2f}: '
      f'{"PASS" if no_stem else "FAIL"}')
ok &= no_stem

stem_path = os.path.join(HERE, 'stem_leaf.stl')
if os.path.exists(stem_path):
    psl, fsl, oksl = report('stem_leaf.stl', shift(load(stem_path),
                                                  BED_Z0['stem_leaf']))
    ok &= oksl
    ok &= ray(psl, fsl, 'leaf hole open', (15.0, -20, 33.3), (0, 1, 0),
              lambda h: not any(-6 < -20 + d < 6 for d in h))
    ok &= ray(psl, fsl, 'leaf wall beside hole', (15.0, -20, 36.5), (0, 1, 0),
              lambda h: any(-6 < -20 + d < 6 for d in h))
else:
    print('stem_leaf.stl: FAIL (missing)')
    ok = False

print('--- complete hollow apple ---')
ok &= ray(pa, fa, 'natural bottom closed', (0, 0, -40), (0, 0, 1),
          lambda h: h and 7 < h[0] < 14)           # sculpted outer underside
ok &= ray(pa, fa, 'hollow above bottom', (0, 0, -40), (0, 0, 1),
          lambda h: len(h) > 1 and 4 < h[1]-h[0] < 10)  # thick natural bottom

print('--- natural bottom shape ---')


def bottom_z(r, deg=0):
    a = math.radians(deg)
    h = hits(pa, fa, (r*math.cos(a), r*math.sin(a), -45), (0, 0, 1))
    return -45 + h[0] if h else None


z0, z8, z26 = (bottom_z(r) for r in (0, 8, 26))
tips = [bottom_z(18, k*72) for k in range(5)]
between = [bottom_z(18, k*72 + 36) for k in range(5)]
deep = z0 is not None and z0 < -29
dimpled = z0 is not None and z8 is not None and z8 < z0 - 1.0
lobes = all(t is not None and m is not None and t < m - 2.0
            for t, m in zip(tips, between))
rounded = z26 is not None and between[0] is not None and z26 > between[0] + 1.0
print(f'  profile r=0/8/26: {[round(v,2) for v in (z0,z8,z26)]}')
print(f'  five soft lobes: tips={[round(v,2) for v in tips]} '
      f'between={[round(v,2) for v in between]}')
print(f'  deep base: {"PASS" if deep else "FAIL"}   '
      f'dimple: {"PASS" if dimpled else "FAIL"}   '
      f'lobes: {"PASS" if lobes else "FAIL"}   '
      f'rounded: {"PASS" if rounded else "FAIL"}')
ok &= deep and dimpled and lobes and rounded

print('--- openings / clearances ---')
ok &= ray(ps, fs, 'OLED active window open', (0, -45, 0), (0, 1, 0),
          lambda h: h and h[0] > 40)                 # front skin removed
ok &= ray(ps, fs, 'shell above window', (0, -45, 10), (0, 1, 0),
          lambda h: h and 0 < h[0] < 27)             # shell starts above 15.0
ok &= ray(ps, fs, 'shell beside window', (17.7, -45, 5), (0, 1, 0),
          lambda h: h and 0 < h[0] < 27)
ok &= ray(ps, fs, 'power hole in back', (0, 45, 12.5), (0, -1, 0),
          lambda h: h and h[0] > 15)                 # back wall is gone
ok &= ray(ps, fs, 'back solid behind display', (0, 45, 0), (0, -1, 0),
          lambda h: h and h[0] < 20)                 # no see-through tunnel
ok &= ray(ps, fs, 'right wall solid at old usb spot', (45, 4.5, 5.5), (-1, 0, 0),
          lambda h: h and h[0] < 15)                 # no usb hole on the side
ok &= ray(ps, fs, 'switch slot in right wall', (45, 0, -2.5), (-1, 0, 0),
          lambda h: h and h[0] > 15)
ok &= ray(ps, fs, 'open at bottom seam', (0, 0, -35), (0, 0, 1),
          lambda h: h and h[0] > 8)                  # no floor at the seam
ok &= ray(pc, fc, 'cap has a floor', (0, 0, -40), (0, 0, 1),
          lambda h: h and h[0] < 18)
cap_z = [(-40 + h[0]) if h else None for r in (0, 8, 18, 26)
         for h in [hits(pc, fc, (r, 0, -40), (0, 0, 1))]]
cap_flat = (all(z is not None and -26.5 < z < -25.0 for z in cap_z) and
            max(cap_z) - min(cap_z) < 0.5)
print(f'  cap flat base: {"PASS" if cap_flat else "FAIL"} '
      f'z={[round(z, 2) if z is not None else None for z in cap_z]}')
ok &= cap_flat

print('--- component envelopes ---')
# The D1 corner sits inside the OLED window, so it has no front wall by design.
for name, x, z, y0, y1, needs_front in (
        ('OLED corner', 17.7, 16.75, -17.5, -13.5, True),
        ('battery corner', 20, 10, 2, 5.4, True),
        ('D1 mini behind window', 12.8, 7.8, -5, -2, False)):
    wall = [-45 + d for d in hits(ps, fs, (x, -45, z), (0, 1, 0))]
    front = max((y for y in wall if y < y0), default=None)
    back = min((y for y in wall if y > y1), default=None)
    good = back is not None and (front is not None or not needs_front)
    print(f'  {name}: {"PASS" if good else "FAIL"} front wall={front} '
          f'part={y0}..{y1} back wall={back}')
    ok &= good

print('--- print bed alignment ---')
for name in ('cap.stl', 'shell.stl', 'stem_leaf.stl'):
    raw = load(os.path.join(HERE, name))
    zmin = min(p[2] for t in raw for p in t)
    good = abs(zmin) < 0.01
    print(f'  {name} lowest z={zmin:.3f}: {"PASS" if good else "FAIL"}')
    ok &= good

print('--- STEP geometry ---')
for name in ('stem_leaf', 'shell', 'cap', 'apple_complete_hollow'):
    path = os.path.join(HERE, name + '.step')
    txt = open(path).read() if os.path.exists(path) else ''
    good = 'MANIFOLD_SOLID_BREP' in txt
    print(f'  {name}.step: {"PASS" if good else "FAIL"}')
    ok &= good

h = hashlib.sha256(open(os.path.join(HERE, 'apple_original.stl'), 'rb').read()).hexdigest()
apple_ok = h == HASH
print(f'  apple unchanged: {"PASS" if apple_ok else "FAIL"}  {h[:16]}')
ok &= apple_ok
print('ALL PASS' if ok else 'FAILURES PRESENT')
sys.exit(0 if ok else 1)
