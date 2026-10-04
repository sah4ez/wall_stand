# -*- coding: utf-8 -*-
"""Держатель малый: открытый лоток 60x55x45 мм.

Печать стоя, без поддержек; дно с перфорацией Ø8.
Пеги 2x2: x=±10, ряды z=30 и -10.
"""
from common import register, plate, mount_pin, finalize, fuse_all, WALL, BOTTOM
import Part
from common import V


@register("small_tray", "Держатель малый (лоток)")
def build():
    p = plate(68, -40, 45)
    pegs = [mount_pin(x, z) for x in (-10, 10) for z in (30, -10)]

    outer = Part.makeBox(60, 55, 45, V(-30, 2, 0))
    inner = Part.makeBox(60 - 2 * WALL, 55 - 2 * WALL, 45 - BOTTOM + 10,
                         V(-30 + WALL, 2 + WALL, BOTTOM))
    shape = fuse_all([p] + pegs + [outer]).cut(inner)

    holes = []
    for hx in (-15, 0, 15):
        for hy in (14, 30, 46):
            holes.append(Part.makeCylinder(4.0, BOTTOM + 2,
                                           V(hx, hy, -1), V(0, 0, 1)))
    for h in holes:
        shape = shape.cut(h)
    return finalize(shape)
