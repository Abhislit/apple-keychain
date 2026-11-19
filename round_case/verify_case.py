"""STL checks for the separate case, plus an unchanged-apple hash check."""
import struct, os, hashlib, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


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
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    print(f'{name}: tris={len(tri)} open={opens} nonmanifold={bad} '
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


pb, fb = report('case_body.stl', load(os.path.join(HERE, 'case_body.stl')))
pl, fl = report('case_lid.stl', load(os.path.join(HERE, 'case_lid.stl')))
ok = True
ok &= ray(pb, fb, 'OLED window', (0, 0, -10), (0, 0, 1),
          lambda h: not h)                           # clean through the floor
ok &= ray(pb, fb, 'OLED recess', (16, 0, -10), (0, 0, 1),
          lambda h: h and abs(h[0]-10) < 0.2)        # solid lip beside window
ok &= ray(pb, fb, 'USB-C slot', (0, 40, 17.5), (0, -1, 0),
          lambda h: h and h[0] > 13)                 # reaches the cavity
ok &= ray(pb, fb, 'switch slot', (40, 0, 11), (-1, 0, 0),
          lambda h: h and h[0] > 12)
h = hashlib.sha256(open(os.path.join(HERE, 'apple_original.stl'), 'rb').read()).hexdigest()
apple_ok = h == '8c2ae8b452da705620cd98764d5ecdc385f55724618e09efbd49740f89dc725e'
print(f'  apple unchanged: {"PASS" if apple_ok else "FAIL"}  {h[:16]}')
ok &= apple_ok
print('ALL PASS' if ok else 'FAILURES PRESENT')
sys.exit(0 if ok else 1)
