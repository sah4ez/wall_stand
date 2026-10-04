# -*- coding: utf-8 -*-
"""Стакан для ручек/карандашей: цилиндр Ø72x95 мм на монтажной пластине.

Печать стоя (дно на столе), без поддержек. Цилиндр утоплен в пластину
на 3 мм: сплавление идёт по хорде стенки ~26 мм шириной на всю высоту,
отдельные рёбра не нужны. Пеги 2x2: x=±10, ряды z=80 и 40.
"""
from common import register, plate, mount_pin, finalize, fuse_all, WALL, BOTTOM
import Part
from common import V


@register("cup", "Стакан для ручек")
def build():
    p = plate(40, 0, 95)
    pegs = [mount_pin(x, z) for x in (-10, 10) for z in (80, 40)]

    cyl_o = Part.makeCylinder(36.0, 95, V(0, 37, 0), V(0, 0, 1))
    cyl_i = Part.makeCylinder(36.0 - WALL, 95 - BOTTOM + 5,
                              V(0, 37, BOTTOM), V(0, 0, 1))
    return finalize(fuse_all([p] + pegs + [cyl_o]).cut(cyl_i))
