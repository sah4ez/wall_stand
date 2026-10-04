# -*- coding: utf-8 -*-
"""Полка 150x72 мм с передним бортиком.

Печать стоя, без поддержек: три треугольных ребра 35° поддерживают
полку по всей глубине. Пеги 3x2: x=-40/0/40, ряды z=±20.
"""
from common import register, plate, mount_pin, prism_x, finalize, fuse_all
import Part
from common import V


@register("shelf", "Полка")
def build():
    p = plate(150, -32, 32)
    pegs = [mount_pin(x, z) for x in (-40, 0, 40) for z in (20, -20)]
    slab = Part.makeBox(150, 72, 4, V(-75, 2, 14))    # y 2..74, z 14..18
    lip = Part.makeBox(150, 6, 10, V(-75, 68, 18))    # y 68..74, z 18..28
    fins = [prism_x([(2, -32), (2, 14), (74, 14)], c - 2, c + 2)
            for c in (-50.0, 0.0, 50.0)]
    return finalize(fuse_all([p] + pegs + [slab, lip] + fins))
