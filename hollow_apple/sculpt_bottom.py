"""Shape the complete hollow apple's flat underside into a natural apple base.

Runs after build_hollow.py. Only the outer bottom skin moves; the inner cavity,
openings and every other part of the apple stay exactly where they are.
"""
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = sys.argv[1] if len(sys.argv) > 1 else 'apple_complete_hollow'
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
        wz = 1 - smooth(-25.5, -24.0, z)      # outer bottom skin only
        dome = 3.0 * (1 - smooth(0, 28, r))    # rounded shoulders
        dimple = 3.0 * (1 - smooth(0, 5, r))   # calyx pit at the centre
        lobe = (3.0 * (0.5 + 0.5 * math.cos(5 * math.atan2(y, x))) *
                smooth(6, 12, r) * (1 - smooth(22, 28, r)))
        z -= wz * (dome + lobe - dimple)
        struct.pack_into('<3f', data, o, x, y, z)
        tri.append((x, y, z))
    a, b, c = tri
    u = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    v = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    nv = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    ln = math.sqrt(sum(k*k for k in nv))
    if ln:
        nv = tuple(k / ln for k in nv)
    struct.pack_into('<3f', data, f, *nv)

with open(PATH, 'wb') as fh:
    fh.write(data)
print(f'sculpted natural bottom into {NAME}.stl ({n} facets)')
