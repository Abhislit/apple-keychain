"""Separate round case that sits BELOW the untouched apple mesh.

The apple STL is not read, scaled or cut. This builds a new 55 mm round puck:
body (open top, electronics loaded from above) + lid with a lip; the apple is
glued to the lid's top. OLED glass faces down through a 30x26 bottom window.
"""
import FreeCAD as App
import Part, Mesh, MeshPart, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
R_OUT, R_IN = 27.5, 25.0            # wall 2.5 mm
BODY_H, FLOOR, LID_H = 20.0, 2.5, 2.0
GROOVE_R, GROOVE_D = 26.4, 1.6
os.makedirs(OUT, exist_ok=True)


def cyl(r, z0, h):
    return Part.makeCylinder(r, h, App.Vector(0, 0, z0))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, App.Vector(x0, y0, z0))


def op(shape, tool, mode, name):
    try:
        out = shape.cut(tool) if mode == 'cut' else shape.fuse(tool)
        print(f'{name}: valid={out.isValid()} solids={len(out.Solids)} '
              f'vol={out.Volume/1000:.2f}', flush=True)
        return out
    except Exception as ex:
        print(f'{name}: FAIL {ex}', flush=True)
        raise SystemExit(9)


# ---------------------------------------------------------------- body
body = op(cyl(R_OUT, 0, BODY_H), cyl(R_IN, FLOOR, BODY_H), 'cut', 'hollow')
# recess in the floor from the inside, then a window through the last 0.7 mm
body = op(body, box(-18.2, 18.2, -17.2, 17.2, 0.7, FLOOR), 'cut', 'oled_recess')
body = op(body, box(-15, 15, -13, 13, -1, 0.71), 'cut', 'window')
# socket groove for the lid lip
groove = cyl(GROOVE_R, BODY_H-GROOVE_D, GROOVE_D).cut(cyl(R_IN, BODY_H-GROOVE_D, GROOVE_D))
body = op(body, groove, 'cut', 'groove')
# USB-C from the back wall, switch from the right wall
body = op(body, box(-4.7, 4.7, 23, 32, 15.5, 20.1), 'cut', 'usb_slot')
body = op(body, box(23, 32, -2.75, 2.75, 8.5, 13.5), 'cut', 'switch_slot')
# shelf for the D1 mini (its edges rest here, OLED back clears it by 0.4 mm)
for sx, tag in ((1, 'R'), (-1, 'L')):
    xa, xb = sorted((sx*16, sx*28))
    body = op(body, box(xa, xb, -13, 13, 7.4, 8.0), 'fuse', f'shelf{tag}')
# keyring fin: runs to the bed, so it prints without supports
fin = box(-6, 6, 26.5, 34.5, 0, BODY_H)
fin = fin.cut(Part.makeCylinder(2.25, 9, App.Vector(0, 26, 17.5), App.Vector(0, 1, 0)))
body = op(body, fin, 'fuse', 'fin')

# ---------------------------------------------------------------- lid
lid = cyl(R_OUT-0.2, BODY_H, LID_H)
lip = cyl(GROOVE_R-0.1, BODY_H-GROOVE_D+0.1, GROOVE_D-0.1)
lip = lip.cut(cyl(R_IN+0.1, BODY_H-GROOVE_D+0.1, GROOVE_D-0.1))
lid = op(lid, lip, 'fuse', 'lid_lip')
# shallow glue ring matching the apple's flat base (~34 mm across)
seat = cyl(17.4, BODY_H+LID_H, 0.7).cut(cyl(16.2, BODY_H+LID_H, 0.7))
lid = op(lid, seat, 'fuse', 'apple_seat')


def save(shape, name):
    shape = shape.removeSplitter()
    print(f'{name}: valid={shape.isValid()} solids={len(shape.Solids)} '
          f'vol={shape.Volume/1000:.2f} bbox={shape.BoundBox}', flush=True)
    Part.export([shape], os.path.join(OUT, name+'.step'))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.4, Relative=False)
    path = os.path.join(OUT, name+'.stl')
    mesh.write(path)
    print(f'  {name}.stl facets={mesh.CountFacets}', flush=True)


save(body, 'case_body')
save(lid, 'case_lid')
print(f'overlap {body.common(lid).Volume:.4f} mm3', flush=True)
print('done', flush=True)
