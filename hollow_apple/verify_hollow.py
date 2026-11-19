"""STL checks for the hollow apple plus an unchanged-source hash check."""
import hashlib
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
    return sorted(out)


def ray(pts, f, label, o, d, ok_fn):
    h = hits(pts, f, o, d)
    ok = bool(ok_fn(h))
    print(f'  {label}: {"PASS" if ok else "FAIL"} dist={[round(x,2) for x in h[:4]]}')
    return ok


ps, fs, ok = report('shell.stl', load(os.path.join(HERE, 'shell.stl')))
pc, fc, okc = report('cap.stl', load(os.path.join(HERE, 'cap.stl')))
ok &= okc

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

print('--- chain-ring hole ---')
ok &= ray(ps, fs, 'leaf hole open', (15.0, -20, 33.3), (0, 1, 0),
          lambda h: not any(-6 < -20 + d < 6 for d in h))
ok &= ray(ps, fs, 'leaf wall beside hole', (15.0, -20, 36.5), (0, 1, 0),
          lambda h: any(-6 < -20 + d < 6 for d in h))

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

h = hashlib.sha256(open(os.path.join(HERE, 'apple_original.stl'), 'rb').read()).hexdigest()
apple_ok = h == HASH
print(f'  apple unchanged: {"PASS" if apple_ok else "FAIL"}  {h[:16]}')
ok &= apple_ok
print('ALL PASS' if ok else 'FAILURES PRESENT')
sys.exit(0 if ok else 1)
