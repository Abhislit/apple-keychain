import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))


def load(p):
    with open(p, 'rb') as fh:
        fh.seek(80)
        n = np.frombuffer(fh.read(4), dtype='<u4')[0]
        raw = np.frombuffer(fh.read(), dtype=np.uint8)[:n*50].reshape(n, 50)
        return raw[:, 12:48].copy().view('<f4').reshape(n, 3, 3).astype(float)


shell = load(os.path.join(HERE, 'shell.stl'))
cap = load(os.path.join(HERE, 'cap.stl'))


def shade(T, light=(0.35, -0.5, 0.8), base=(0.85, 0.30, 0.28)):
    n = np.cross(T[:, 1]-T[:, 0], T[:, 2]-T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    l = np.array(light, float); l /= np.linalg.norm(l)
    s = np.abs(n @ l)
    return np.clip(np.array(base)[None, :] * (0.35 + 0.85*s[:, None]), 0, 1)


fig = plt.figure(figsize=(15, 12))
views = [(16, -70, 'iso'), (0, -90, 'front'), (0, 0, 'top'), (90, -90, 'side')]
allT = np.concatenate([shell, cap])
mn, mx = allT.reshape(-1, 3).min(0), allT.reshape(-1, 3).max(0)
ctr, rad = (mn+mx)/2, (mx-mn).max()/2
for i, (el, az, name) in enumerate(views, 1):
    ax = fig.add_subplot(2, 2, i, projection='3d')
    for T, col in ((shell, (0.85, 0.30, 0.28)), (cap, (0.30, 0.45, 0.85))):
        ax.add_collection3d(Poly3DCollection(T, facecolors=shade(T, base=col),
                                            edgecolor='none'))
    ax.set_xlim(ctr[0]-rad, ctr[0]+rad); ax.set_ylim(ctr[1]-rad, ctr[1]+rad)
    ax.set_zlim(ctr[2]-rad, ctr[2]+rad)
    ax.set_box_aspect([1, 1, 1]); ax.view_init(el, az); ax.set_title(name)
    ax.set_xlabel('X'); ax.set_ylabel('Y (depth)'); ax.set_zlabel('Z')
plt.tight_layout(); plt.savefig(os.path.join(HERE, 'views.png'), dpi=110)
print('views saved')


def section(T, axis, val):
    au, av = [a for a in (0, 1, 2) if a != axis]
    segs = []
    d = T[:, :, axis] - val
    for i in range(len(T)):
        if (d[i] > 0).any() and (d[i] < 0).any():
            p = []
            for a, b in ((0, 1), (1, 2), (2, 0)):
                if (d[i, a] > 0) != (d[i, b] > 0):
                    t = d[i, a] / (d[i, a] - d[i, b])
                    p.append(T[i, a] + t*(T[i, b]-T[i, a]))
            if len(p) >= 2:
                segs.append([(p[0][au], p[0][av]), (p[-1][au], p[-1][av])])
    return segs


fig, axs = plt.subplots(2, 1, figsize=(13, 10))
for ax, (axis, val, xl, yl, title) in zip(axs, [
        (0, 0.0, 'Y depth', 'Z', 'section X=0'),
        (2, 0.0, 'X', 'Y depth', 'section Z=0')]):
    for T, col in ((shell, 'crimson'), (cap, 'royalblue')):
        for s in section(T, axis, val):
            ax.plot([s[0][0], s[1][0]], [s[0][1], s[1][1]], color=col, lw=0.7)
    ax.set_aspect('equal'); ax.grid(True, alpha=.3)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title)
plt.tight_layout(); plt.savefig(os.path.join(HERE, 'sections.png'), dpi=110)
print('sections saved')
