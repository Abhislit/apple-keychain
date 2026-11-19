"""Sculpt three smooth calyx lobes into the base of full_bottom.stl.

Runs after build_full_bottom.py. Displacement depends only on position, so
coincident vertices move together and the mesh stays watertight.
"""
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = sys.argv[1] if len(sys.argv) > 1 else 'full_bottom'
LOBES = int(sys.argv[2]) if len(sys.argv) > 2 else 3
DEPTH = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
PATH = os.path.join(HERE, NAME + '.stl')


def smooth(a, b, t):
    u = max(0.0, min(1.0, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)


data = bytearray(open(PATH, 'rb').read())
n = struct.unpack_from('<I', data, 80)[0]
for i in range(n):
    f = 84 + 50 * i
    tri = []
    for v in range(3):
        o = f + 12 + 12 * v
        x, y, z = struct.unpack_from('<3f', data, o)
        r = math.hypot(x, y)
        lobe = 0.5 + 0.5 * math.cos(LOBES * math.atan2(y, x))
        weight = (smooth(6, 12, r) * (1 - smooth(22, 28, r)) *
                  max(0.0, min(1.0, (-24 - z) / 4)))
        z = z - DEPTH * lobe * weight
        struct.pack_into('<3f', data, o, x, y, z)
        tri.append((x, y, z))
    a, b, c = tri
    u = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    v = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    nv = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    ln = math.sqrt(sum(k*k for k in nv))
    if ln:
        nv = tuple(k/ln for k in nv)
    struct.pack_into('<3f', data, f, *nv)

with open(PATH, 'wb') as fh:
    fh.write(data)
print(f'sculpted {n} facets, {LOBES} lobes, {DEPTH} mm deep')
