"""Apple keychain enclosure - built from the supplied apple mesh.

The apple's own outer surface (body + stem/leaf) is the shell: no loft. It is
scaled to 60 mm wide, squashed to 22.5 mm deep, hollowed with an inward-scaled
copy of itself, and closed by a 5 mm cap cut from the bottom. The only openings
are the screen window, the switch slot, the USB-C tunnel and the seam.

Frame: X right, Y depth (0 = front), Z up (0 = body mid-height).
Print: shell seam-down, cap bottom-down.
"""
import FreeCAD as App
import Part, Mesh, MeshPart, math, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'obj_1_Assembly.stl')
OUT = os.path.join(HERE, 'build')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- params
W, T = 60.0, 35.0                 # outer width / depth
CAP_H = 5.0                       # cap height (seam above the bottom)
PLATE_Y = 4.8                     # OLED front plane = window back plane
POCKET_D = 3.4                    # front recess for the 35.4x33.5 OLED
CAV_Y0, CAV_Y1 = PLATE_Y + POCKET_D, T - 3.0  # cavity, 3 mm back wall
POCKET_W, POCKET_H = 37.0, 35.0   # OLED (35.4x33.5) + clearance
WIN_W, WIN_H = 30.0, 26.0

LIP_CLEAR, LIP_T, LIP_H = 0.04, 1.2, 1.9
LIP_EMBED = 0.6                   # lip root sunk into the cap for a solid fuse

D1_W, D1_H, D1_F, D1_B = 34.2, 25.6, 15.1, 19.8
D1_Z0, D1_Z1 = -12.6, 13.0
TP_W, TP_H, TP_F, TP_B = 19.5, 26.5, 11.5, 14.9  # 19.5 edge down, USB-C down

BAT_W, BAT_H, BAT_T = 40.0, 20.0, 3.4
BAT_Y0, BAT_Y1 = 20.0, 23.4
SW_L, SW_H, SW_W = 8.7, 3.5, 4.4
SW_Z, SW_Y = -4.0, 15.25

BAIL_W, BAIL_Y0, BAIL_Y1 = 13.0, T - 7.0, T
BAIL_TOP, HOLE_Z, HOLE_D = 28.75, 28.75, 4.5

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
S = W / (max(xs) - min(xs))
SY = T / (max(ys) - min(ys))
ZBOT, ZTOP = -T * 0 + (min(zs) - cz) * S, (max(zs) - cz) * S
ZCUT = ZBOT + CAP_H
print(f'scale {S:.4f} y {SY:.4f}  z {ZBOT:.2f}..{ZTOP:.2f}  cut {ZCUT:.2f}', flush=True)

# ---------------------------------------------------------------- solids
def build_solid(ids, fcs, coords):
    idx = {v: n for n, v in enumerate(ids)}
    sp = [App.Vector(*coords[v]) for v in ids]
    sf = [tuple(idx[i] for i in f) for f in fcs]
    sh = Part.Shape()
    sh.makeShapeFromMesh((sp, sf), 0.05, True)
    solids = [Part.Solid(s) for s in sh.Shells]
    return max(solids, key=lambda s: s.Volume)

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))

def op(shape, tool, mode, name):
    try:
        out = shape.cut(tool) if mode == 'cut' else shape.fuse(tool)
        print(f'  op {name}: ok={out.isValid()} solids={len(out.Solids)} '
              f'vol={out.Volume/1000:.2f}', flush=True)
        return out
    except Exception as ex:
        print(f'  op {name}: FAIL {ex}', flush=True)
        raise SystemExit(9)

BODY = {i: ((pts[i][0] - cx) * S,
            (pts[i][1] - cy) * SY + T / 2,
            (pts[i][2] - cz) * S) for i in body_ids}
STEM = {i: ((pts[i][0] - cx) * S,
            (pts[i][1] - cy) + T / 2,
            (pts[i][2] - cz) * S - 0.6) for i in stem_ids}
# hollow: 2.4 mm walls at the widest point
CAV = {i: (BODY[i][0] * 0.92,
           (BODY[i][1] - T / 2) * 0.787 + T / 2,
           BODY[i][2] * 0.896) for i in body_ids}

body = build_solid(body_ids, body_faces, BODY)
print(f'body valid={body.isValid()} vol={body.Volume/1000:.2f} '
      f'bbox={body.BoundBox}', flush=True)
stem = build_solid(stem_ids, stem_faces, STEM)
print(f'stem valid={stem.isValid()} vol={stem.Volume/1000:.2f}', flush=True)
body = op(body, stem, 'fuse', 'stem')

inner = build_solid(body_ids, body_faces, CAV)
cavity = inner.common(box(-300, 300, CAV_Y0, CAV_Y1, -300, 300))
print(f'cavity valid={cavity.isValid()} solids={len(cavity.Solids)} '
      f'vol={cavity.Volume/1000:.2f} y={cavity.BoundBox.YMin:.2f}'
      f'..{cavity.BoundBox.YMax:.2f}', flush=True)

shell = op(body, cavity, 'cut', 'cavity')

# screen: window through the curved front, flat pocket behind it
shell = op(shell, box(-POCKET_W/2, POCKET_W/2, PLATE_Y, CAV_Y0,
                      -POCKET_H/2, POCKET_H/2), 'cut', 'pocket')
shell = op(shell, box(-WIN_W/2, WIN_W/2, -1, PLATE_Y,
                      -WIN_H/2, WIN_H/2), 'cut', 'window')

# ---------------------------------------------------------------- ledges
TP_Z0, TP_Z1 = ZCUT + 0.1, ZCUT + 0.1 + TP_H
ZG0 = ZCUT + LIP_H + 0.2
BODY_BOX = box(-300, 300, -300, 300, -300, 300)

for sx, tag in ((1, 'R'), (-1, 'L')):
    xa, xb = sorted((sx * 16.0, sx * 45.0))
    tab = box(xa, xb, D1_B - 0.9, D1_B, D1_Z0 - 0.6, D1_Z1 + 0.6).common(body)
    shell = op(shell, tab, 'fuse', f'shelf{tag}')
for sx, tag in ((1, 'R'), (-1, 'L')):
    xa, xb = sorted((sx * 17.2, sx * 18.5))
    shell = op(shell, box(xa, xb, D1_F, D1_B - 0.7, D1_Z0 - 0.6, D1_Z1 + 0.6),
               'fuse', f'd1guide{tag}')

# switch slot last: it may trim shelf material
shell = op(shell, box(22.0, 60, SW_Y - SW_H/2 - 0.3, SW_Y + SW_H/2 + 0.3,
                      SW_Z - SW_L/2 - 0.3, SW_Z + SW_L/2 + 0.3), 'cut', 'switch')

# ---------------------------------------------------------------- bail
bail = box(-BAIL_W/2, BAIL_W/2, BAIL_Y0, BAIL_Y1, 12.0, HOLE_Z)
bail = bail.fuse(Part.makeCylinder(BAIL_W/2, BAIL_Y1 - BAIL_Y0,
                                   App.Vector(0, BAIL_Y0, HOLE_Z), App.Vector(0, 1, 0)))
bail = bail.cut(Part.makeCylinder(HOLE_D/2, BAIL_Y1 - BAIL_Y0 + 2,
                                  App.Vector(0, BAIL_Y0 - 1, HOLE_Z), App.Vector(0, 1, 0)))
bail = bail.cut(cavity)          # never fill the compartment
shell = op(shell, bail, 'fuse', 'bail')

# ---------------------------------------------------------------- split
shell = shell.common(box(-300, 300, -300, 300, ZCUT, 300))
cap = body.common(box(-300, 300, -300, 300, -300, ZCUT))
print(f'shell {len(shell.Solids)} {shell.Volume/1000:.2f}  '
      f'cap {len(cap.Solids)} {cap.Volume/1000:.2f}', flush=True)

# ---------------------------------------------------------------- lip
slab = cavity.common(box(-300, 300, CAV_Y0, CAV_Y1, ZCUT - 0.01, ZCUT + 0.01))
flat = [f for f in slab.Faces if abs(f.normalAt(0, 0).z) > 0.99]
sect = max(flat, key=lambda f: f.Area)
# makeOffset2D returns the band between the wire and its offset, so the lip
# ring is the wide band minus the thin one
band_out = sect.makeOffset2D(-LIP_CLEAR, 0, True, False)
band_in = sect.makeOffset2D(-(LIP_CLEAR + LIP_T), 0, True, False)
ring = band_in.cut(band_out)
print(f'lip section area {sect.Area:.1f} ring {ring.Area:.1f}', flush=True)
lip = ring.extrude(App.Vector(0, 0, LIP_H + LIP_EMBED))
lip.translate(App.Vector(0, 0, ZCUT - LIP_EMBED - lip.BoundBox.ZMin))
cap = op(cap, lip, 'fuse', 'lip')

cap = op(cap, box(-4.7, 4.7, TP_F - 0.4, TP_B + 0.4,
                  ZBOT - 1.0, ZCUT + 0.15), 'cut', 'usb')
cap = op(cap, box(-5, 5, T - 2.1, T + 0.5, ZCUT - 1.6, ZCUT - 0.02), 'cut', 'pry')
print(f'cap {len(cap.Solids)} {cap.Volume/1000:.2f}', flush=True)

# ---------------------------------------------------------------- export
def save(shape, name):
    shape = shape.removeSplitter()
    print(f'{name}: valid={shape.isValid()} solids={len(shape.Solids)} '
          f'vol={shape.Volume/1000:.2f}cm3 bbox={shape.BoundBox}', flush=True)
    Part.export([shape], os.path.join(OUT, name + '.step'))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.4, Relative=False)
    path = os.path.join(OUT, name + '.stl')
    mesh.write(path)
    chk = Mesh.Mesh(path)
    try:
        ok = chk.isSolid()
    except Exception:
        ok = 'n/a'
    print(f'   facets {chk.CountFacets} solid={ok}', flush=True)

save(shell, 'front')
save(cap, 'base')
inter = shell.common(cap)
print(f'overlap vol={inter.Volume:.4f} mm3', flush=True)

json.dump({'W': W, 'T': T, 'CAP_H': CAP_H, 'ZBOT': ZBOT, 'ZCUT': ZCUT,
           'PLATE_Y': PLATE_Y, 'CAV_Y0': CAV_Y0, 'CAV_Y1': CAV_Y1,
           'POCKET_W': POCKET_W, 'POCKET_H': POCKET_H,
           'WIN_W': WIN_W, 'WIN_H': WIN_H, 'LIP_H': LIP_H,
           'OLED_W': 35.4, 'OLED_H': 33.5,
           'D1_F': D1_F, 'D1_B': D1_B, 'TP_F': TP_F, 'TP_B': TP_B,
           'TP_Z0': TP_Z0, 'TP_Z1': TP_Z1,
           'BAT_T': BAT_T, 'BAT_Y0': BAT_Y0, 'BAT_Y1': BAT_Y1},
          open(os.path.join(OUT, 'params.json'), 'w'), indent=1)
print('done', flush=True)
