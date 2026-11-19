"""Render a model on a white studio background (two views)."""
import math
import os
import struct
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = sys.argv[1] if len(sys.argv) > 1 else 'apple_base_five'
d = open(os.path.join(HERE, NAME + '.stl'), 'rb').read()
n = struct.unpack('<I', d[80:84])[0]
tri = []
for i in range(n):
    v = struct.unpack('<12fH', d[84+50*i:84+50*i+50])
    tri.append([(v[3], v[4], v[5]), (v[6], v[7], v[8]), (v[9], v[10], v[11])])

t = np.array(tri)
a, b, c = t[:, 0], t[:, 1], t[:, 2]
norm = np.cross(b-a, c-a)
ln = np.linalg.norm(norm, axis=1)
norm[ln > 0] /= ln[ln > 0, None]
light = np.array([0.35, -0.65, 0.67])
light /= np.linalg.norm(light)
shade = np.clip(np.abs(norm @ light), 0, 1) * 0.55 + 0.45
colors = np.stack([shade*0.93, shade*0.58, shade*0.37], axis=1)

fig = plt.figure(figsize=(11, 6), facecolor='white')
for k, (el, az, title) in enumerate(((28, -55, 'three-quarter'),
                                     (-78, -90, 'underside — five calyx lobes'))):
    ax = fig.add_subplot(1, 2, k+1, projection='3d')
    ax.set_facecolor('white')
    pc = Poly3DCollection(tri, facecolors=colors, edgecolor='none', shade=False)
    ax.add_collection3d(pc)
    ax.set_xlim(-35, 35); ax.set_ylim(-35, 35); ax.set_zlim(-32, 4)
    ax.set_box_aspect((70, 70, 36))
    ax.view_init(elev=el, azim=az)
    ax.set_title(title, color='#333', fontsize=11)
    ax.set_axis_off()
    ax.grid(False)
plt.tight_layout()
out = os.path.join(HERE, NAME + '_render.png')
plt.savefig(out, dpi=130, facecolor='white')
print('saved', out)
