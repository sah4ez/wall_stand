# -*- coding: utf-8 -*-
"""Держатель наушников: опорная полка с упорной губкой.

Оголовье ложится на горизонтальную площадку, чашки висят перед панелью.
Печать стоя, без поддержек: опорный клин 45°, губка — вертикальная стенка.
Пеги 2x2: x=±20, ряды z=±20.
"""
from common import register, plate, mount_pin, prism_x, finalize, fuse_all
import Part
from common import V


@register("headband_holder", "Держатель наушников")
def build():
    p = plate(90, -32, 32)
    pegs = [mount_pin(x, z) for x in (-20, 20) for z in (20, -20)]
    wedge = prism_x([(2, -6), (2, 26), (44, 26)], -30, 30)  # гипотенуза 37°
    slab = Part.makeBox(60, 42, 4, V(-30, 2, 26))     # y 2..44, z 26..30
    lip = Part.makeBox(60, 6, 14, V(-30, 38, 30))     # y 38..44, z 30..44
    return finalize(fuse_all([p] + pegs + [wedge, slab, lip]))
