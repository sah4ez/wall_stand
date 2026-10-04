# -*- coding: utf-8 -*-
"""Корзина 120x70x55 мм: открытый короб, тыльной стенкой крепится к панели.

Днище с перфорацией Ø8 (визуальный ритм панели + экономия пластика).
Печать стоя, без поддержек. Пеги 2x2: x=±20, ряды z=35 и -5.
"""
from common import register, plate, mount_pin, finalize, fuse_all, WALL, BOTTOM
import Part
from common import V


@register("basket", "Корзина")
def build():
    p = plate(128, -40, 55)
    pegs = [mount_pin(x, z) for x in (-20, 20) for z in (35, -5)]

    outer = Part.makeBox(120, 70, 55, V(-60, 2, 0))
    inner = Part.makeBox(120 - 2 * WALL, 70 - 2 * WALL, 55 - BOTTOM + 10,
                         V(-60 + WALL, 2 + WALL, BOTTOM))
    shape = fuse_all([p] + pegs + [outer]).cut(inner)

    holes = []
    for hx in (-40, -20, 0, 20, 40):
        for hy in (14, 30, 46):
            holes.append(Part.makeCylinder(4.0, BOTTOM + 2,
                                           V(hx, hy, -1), V(0, 0, 1)))
    for h in holes:
        shape = shape.cut(h)
    return finalize(shape)
