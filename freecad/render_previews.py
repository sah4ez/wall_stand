# -*- coding: utf-8 -*-
"""Превью-рендеры STL-файлов (без FreeCAD): numpy + matplotlib.

Запуск: uv run --with numpy --with matplotlib python render_previews.py
"""
import os
import struct

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL_DIR = os.path.join(ROOT, "output", "stl")
OUT_DIR = os.path.join(ROOT, "output", "views")


def load_stl(path):
    with open(path, "rb") as f:
        header = f.read(80)
        if header[:5].lower() == b"solid":
            raise ValueError("text STL not expected")
        (n,) = struct.unpack("<I", f.read(4))
        tris = np.empty((n, 3, 3))
        for i in range(n):
            f.read(12)  # normal
            for v in range(3):
                tris[i, v] = struct.unpack("<3f", f.read(12))
            f.read(2)  # attr
        return tris


def render(name):
    tris = load_stl(os.path.join(STL_DIR, name + ".stl"))
    # сдвиг к началу координат для плотной кадрировки
    tris -= tris.reshape(-1, 3).min(axis=0)

    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    light = np.array([0.4, -0.5, 0.75])
    light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.6 + 0.35

    fig = plt.figure(figsize=(7, 6), dpi=110)
    ax = fig.add_subplot(projection="3d")
    coll = Poly3DCollection(tris, facecolors=plt.cm.Blues(shade * 0.75 + 0.15),
                            edgecolor="none")
    ax.add_collection3d(coll)
    pts = tris.reshape(-1, 3)
    mx = pts.max(axis=0)
    ax.set_xlim(0, mx[0]), ax.set_ylim(0, mx[1]), ax.set_zlim(0, mx[2])
    ax.set_box_aspect(tuple(mx / max(mx)))
    ax.view_init(elev=22, azim=125)  # вид спереди-слева (функциональная сторона +Y)
    ax.set_axis_off()
    ax.set_title(name, fontsize=10)
    out = os.path.join(OUT_DIR, name + ".png")
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


os.makedirs(OUT_DIR, exist_ok=True)
for fn in sorted(os.listdir(STL_DIR)):
    if fn.endswith(".stl"):
        print("VIEW", render(fn[:-4]))
print("VIEWS_DONE")
