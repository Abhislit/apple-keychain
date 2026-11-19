"""Standalone STL checks: watertightness, components, volume, key openings."""
import struct, sys, os, math
from collections import defaultdict

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')

def load(path):
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    tri = []
    for i in range(n):
        v = struct.unpack('<12fH', d[84 + 50*i: 84 + 50*i + 50])
        tri.append(((v[3], v[4], v[5]), (v[6], v[7], v[8]), (v[9], v[10], v[11])))
    return tri

def weld(tri, q=1e-4):
    ids, pts = {}, []
    def idx(p):
        k = (round(p[0]/q), round(p[1]/q), round(p[2]/q))
        if k not in ids:
            ids[k] = len(pts); pts.append(p)
        return ids[k]
    f = [tuple(idx(p) for p in t) for t in tri]
    return pts, f

def volume(tri):
    return sum((a[0]*(b[1]*c[2]-b[2]*c[1])
                - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6 for a, b, c in tri)

def report(name, tri):
    pts, f = weld(tri)
    edges = defaultdict(int)
    for t in f:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges[(min(a, b), max(a, b))] += 1
    opens = sum(1 for n in edges.values() if n == 1)
    bad = sum(1 for n in edges.values() if n > 2)
    # components over welded points
    par = list(range(len(pts)))
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for t in f:
        for b in t[1:]:
            ra, rb = find(t[0]), find(b)
            if ra != rb:
                par[ra] = rb
    comps = len({find(i) for i in range(len(pts))})
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    print(f'{name}: tris={len(tri)} comps={comps} open={opens} nonmanifold={bad} '
          f'vol={volume(tri)/1000:.2f}cm3 '
          f'x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}] '
          f'z[{min(zs):.1f},{max(zs):.1f}]')
    return pts, f

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
        u = sum(s[i]*p[i] for i in range(3)) / det
        if u < -1e-9 or u > 1+1e-9:
            continue
        q = [s[1]*e1[2]-s[2]*e1[1], s[2]*e1[0]-s[0]*e1[2], s[0]*e1[1]-s[1]*e1[0]]
        v = sum(d[i]*q[i] for i in range(3)) / det
        if v < -1e-9 or u+v > 1+1e-9:
            continue
        w = sum(e2[i]*q[i] for i in range(3)) / det
        if w > 0:
            out.append(w)                      # distance along the unit ray
    return sorted(out)

def ray(pts, f, label, o, d, expect):
    h = hits(pts, f, o, d)
    ok = expect(h)
    print(f'  {label}: {"PASS" if ok else "FAIL"} '
          f'dist={[round(x,2) for x in h[:4]]}')
    return ok

print('--- front (shell) ---')
pf, ff = report('front.stl', load(os.path.join(B, 'front.stl')))
print('--- base (cap) ---')
pb, fb = report('base.stl', load(os.path.join(B, 'base.stl')))
print('--- openings ---')
ok = True
# window centre: first skin at y>4.9 (ray starts at y=-10)
ok &= ray(pf, ff, 'window open', (0, -10, 0), (0, 1, 0),
          lambda h: h and h[0] > 25)
# switch slot: right wall (x 20..50) is absent; first hit is the D1 guide
ok &= ray(pf, ff, 'switch open', (50, 15.25, -4), (-1, 0, 0),
          lambda h: not any(0 < d < 30 for d in h))
# cap USB tunnel: straight through, no material
ok &= ray(pb, fb, 'usb tunnel', (0, 13, -40), (0, 0, 1),
          lambda h: not h)
# lip front band: the cap's top surface at y=6.8 is 1.9 mm above the seam
ok &= ray(pb, fb, 'lip present', (0, 8.8, -40), (0, 0, 1),
          lambda h: h and h[-1] > 23.5)
print('ALL PASS' if ok else 'FAILURES PRESENT')
sys.exit(0 if ok else 1)
