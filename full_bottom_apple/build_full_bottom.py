"""Solid bottom half of the apple: original shape, uniform scale, no internals.

Only the body's lower half (z <= 0 after centering) is kept. There is no
cavity, shelf, tab, window or hole, and no stem/leaf. The source apple is
never modified. Runs: snap run freecad.cmd ./build_full_bottom.py
"""
import FreeCAD as App
import Part, Mesh, MeshPart, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'apple_original.stl')
OUT = HERE
S = 1.50          # same uniform scale as the hollow model

m = Mesh.Mesh(SRC)
pts = [[p.x, p.y, p.z] for p in m.Points]
faces = [tuple(f.PointIndices) for f in m.Facets]
parent = list(range(len(pts)))


def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


for f in faces:
    for b in f[1:]:
        ra, rb = find(f[0]), find(b)
        if ra != rb:
            parent[ra] = rb
comp = {}
for i in range(len(pts)):
    comp.setdefault(find(i), []).append(i)
body_ids = min(comp.values(), key=lambda ids: min(pts[i][2] for i in ids))
bset = set(body_ids)
body_faces = [f for f in faces if f[0] in bset]

xs = [pts[i][0] for i in body_ids]
ys = [pts[i][1] for i in body_ids]
zs = [pts[i][2] for i in body_ids]
cx = (min(xs) + max(xs)) / 2
cy = (min(ys) + max(ys)) / 2
cz = (min(zs) + max(zs)) / 2
coords = {i: ((pts[i][0] - cx) * S, (pts[i][1] - cy) * S,
              (pts[i][2] - cz) * S) for i in body_ids}

idx = {v: n for n, v in enumerate(body_ids)}
sp = [App.Vector(*coords[v]) for v in body_ids]
sf = [tuple(idx[i] for i in f) for f in body_faces]
sh = Part.Shape()
sh.makeShapeFromMesh((sp, sf), 0.05, True)
body = max([Part.Solid(s) for s in sh.Shells], key=lambda s: s.Volume)
print(f'body: valid={body.isValid()} vol={body.Volume/1000:.2f} '
      f'bbox={body.BoundBox}', flush=True)

# keep everything at or below z=0 -> the complete lower half of the apple
lower = body.common(Part.makeBox(300, 300, 150, App.Vector(-150, -150, -150)))
# Do not removeSplitter(): the source mesh has coincident facets and that
# operation turns this otherwise valid solid invalid.
print(f'lower half: valid={lower.isValid()} solids={len(lower.Solids)} '
      f'vol={lower.Volume/1000:.2f} bbox={lower.BoundBox}', flush=True)
if not lower.isValid() or len(lower.Solids) != 1:
    raise SystemExit(9)

Part.export([lower], os.path.join(OUT, 'full_bottom.step'))
mesh = MeshPart.meshFromShape(Shape=lower, LinearDeflection=0.06,
                              AngularDeflection=0.4, Relative=False)
path = os.path.join(OUT, 'full_bottom.stl')
mesh.write(path)
chk = Mesh.Mesh(path)
print(f'full_bottom.stl facets={chk.CountFacets}', flush=True)
