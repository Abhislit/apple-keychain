"""Hollow apple: original mesh, uniform scale, no shape change.

The outer body and stem are uniformly scaled by S. The cavity is the same
mesh scaled uniformly by S*K. Nothing is squashed or lofted; the apple keeps
its exact round shape. Runs: snap run freecad.cmd ./build_hollow.py
"""
import FreeCAD as App
import Part, Mesh, MeshPart, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'apple_original.stl')
OUT = HERE

S = 1.50            # uniform outer scale (shape preserved)
K = 0.90            # inner cavity as a fraction of the scaled outer
SEAM_Z = -20.0      # cap is everything below this flat seam
WIN_X, WIN_Z = 14.86, 7.50   # active area 29.42 x 14.7 + 0.2 mm clearance/side
OLED_F = -17.5      # OLED front plane
os.makedirs(OUT, exist_ok=True)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def op(shape, tool, mode, name):
    try:
        out = shape.cut(tool) if mode == 'cut' else shape.fuse(tool)
        print(f'  {name}: valid={out.isValid()} solids={len(out.Solids)} '
              f'vol={out.Volume/1000:.2f}', flush=True)
        return out
    except Exception as ex:
        print(f'  {name}: FAIL {ex}', flush=True)
        raise SystemExit(9)


# ---------------------------------------------------------------- mesh read
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
stem_ids = max(comp.values(), key=lambda ids: len(ids))
bset = set(body_ids)
body_faces = [f for f in faces if f[0] in bset]
stem_faces = [f for f in faces if f[0] not in bset]

xs = [pts[i][0] for i in body_ids]
ys = [pts[i][1] for i in body_ids]
zs = [pts[i][2] for i in body_ids]
cx = (min(xs) + max(xs)) / 2
cy = (min(ys) + max(ys)) / 2
cz = (min(zs) + max(zs)) / 2

BODY = {i: ((pts[i][0] - cx) * S, (pts[i][1] - cy) * S,
            (pts[i][2] - cz) * S) for i in body_ids}
STEM = {i: ((pts[i][0] - cx) * S, (pts[i][1] - cy) * S,
            (pts[i][2] - cz) * S - 0.6) for i in stem_ids}
CAV = {i: (BODY[i][0] * K, BODY[i][1] * K, BODY[i][2] * K) for i in body_ids}
print(f'body dia={S*(max(xs)-min(xs)):.2f} z=[{min(BODY[i][2] for i in body_ids):.2f},'
      f'{max(BODY[i][2] for i in body_ids):.2f}] cavity dia={S*K*(max(xs)-min(xs)):.2f}',
      flush=True)


def build_solid(ids, fcs, coords):
    idx = {v: n for n, v in enumerate(ids)}
    sp = [App.Vector(*coords[v]) for v in ids]
    sf = [tuple(idx[i] for i in f) for f in fcs]
    sh = Part.Shape()
    sh.makeShapeFromMesh((sp, sf), 0.05, True)
    return max([Part.Solid(s) for s in sh.Shells], key=lambda s: s.Volume)


# ---------------------------------------------------------------- shell
body = build_solid(body_ids, body_faces, BODY)
stem_leaf = build_solid(stem_ids, stem_faces, STEM)
# 5 mm chain-ring hole through the thickest part of the leaf (right prong)
stem_leaf = op(stem_leaf, Part.makeCylinder(2.5, 20, App.Vector(15.0, -10, 33.3),
                                           App.Vector(0, 1, 0)),
               'cut', 'leaf_hole')
# the source component is open where it met the body; close that tiny base
stem_leaf = op(stem_leaf, box(-1.5, 2.0, -4.5, -3.0, 20.2, 21.0),
               'fuse', 'stem_base')
inner = build_solid(body_ids, body_faces, CAV)
shell = op(body, inner, 'cut', 'cavity')

# front window: only the 29.42 x 14.7 active display area
shell = op(shell, box(-WIN_X, WIN_X, -40, OLED_F - 0.3, -WIN_Z, WIN_Z),
           'cut', 'window')
# TP4056 power: small rectangle in the back wall, above the display window
# so the two openings never line up into a see-through tunnel
shell = op(shell, box(-5, 5, 24, 42, 10, 15), 'cut', 'power_back')
# slide switch actuator: narrow slot in the right wall
shell = op(shell, box(26, 45, -4.5, 4.5, -4, -1), 'cut', 'switch')

# OLED edge tabs, embedded in the side walls so they fuse cleanly
for sx, tag in ((1, 'R'), (-1, 'L')):
    xa, xb = sorted((sx * 14.0, sx * 20.0))
    tab = box(xa, xb, -19, -12, -18.5, -16.8).common(body)
    if tab.Volume > 0:
        shell = op(shell, tab, 'fuse', f'oled_tab{tag}')

# platform for the boards and battery; the rim sinks into the wall
plat = box(-24, 24, -11, 20, -9.2, -7.8).common(body)
if plat.Volume > 0:
    shell = op(shell, plat, 'fuse', 'platform')

# ---------------------------------------------------------------- split
parts = shell.common(box(-300, 300, -300, 300, SEAM_Z, 300))
cap = shell.common(box(-300, 300, -300, 300, -300, SEAM_Z))
print(f'shell solids={len(parts.Solids)} vol={parts.Volume/1000:.2f}  '
      f'cap solids={len(cap.Solids)} vol={cap.Volume/1000:.2f}', flush=True)

# Only the one-piece complete apple gets the rounded natural bottom. The
# two-piece shell + cap keep the original flat seam so the cap prints flat.
z_base = min(BODY[i][2] for i in body_ids)
d, r_rim = 7.0, 27.5
R = (r_rim*r_rim + d*d) / (2*d)
zc = z_base - d + R
bottom = Part.makeSphere(R, App.Vector(0, 0, zc)).common(
    Part.makeCylinder(r_rim, 12.5, App.Vector(0, 0, z_base - 12)))
complete = op(shell, bottom, 'fuse', 'natural_bottom')
a, depth = 5.0, 3.0
c = (a*a - depth*depth) / (2*depth)
complete = op(complete, Part.makeSphere(c + depth,
                                       App.Vector(0, 0, z_base - d - c)),
              'cut', 'calyx_dimple')
complete = complete.removeSplitter()


def save(shape, name, to_bed=False):
    shape = shape.removeSplitter()
    if to_bed:
        shape.translate(App.Vector(0, 0, -shape.BoundBox.ZMin))
    print(f'{name}: valid={shape.isValid()} solids={len(shape.Solids)} '
          f'vol={shape.Volume/1000:.2f} bbox={shape.BoundBox}', flush=True)
    shape.exportStep(os.path.join(OUT, name + '.step'))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.06,
                                  AngularDeflection=0.4, Relative=False)
    path = os.path.join(OUT, name + '.stl')
    mesh.write(path)
    chk = Mesh.Mesh(path)
    print(f'   {name}.stl facets={chk.CountFacets}', flush=True)


# the complete apple is hollow inside with a natural bottom; shell + cap stay flat
save(complete, 'apple_complete_hollow')
save(parts, 'shell', to_bed=True)
save(cap, 'cap', to_bed=True)
save(stem_leaf, 'stem_leaf', to_bed=True)
print(f'overlap vol={parts.common(cap).Volume:.4f} mm3', flush=True)
print('done', flush=True)
