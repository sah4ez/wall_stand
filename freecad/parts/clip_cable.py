# -*- coding: utf-8 -*-
"""Клипса для кабеля: разомкнутое кольцо с продольным пазом (кабель Ø3–7).

Печать стоя, без поддержек. Горизонтальная пара пегов x=±10 (шаг 20).
"""
from common import register, plate, mount_pin, finalize, fuse_all
import Part
from common import V


@register("clip_cable", "Клипса для кабеля")
def build():
    p = plate(44, -20, 20)
    pegs = [mount_pin(x, 0) for x in (-10, 10)]

    ring_o = Part.makeCylinder(8.0, 12, V(0, 16, -6), V(0, 0, 1))
    ring_i = Part.makeCylinder(4.25, 14, V(0, 16, -7), V(0, 0, 1))
    web = Part.makeBox(8, 10, 12, V(-4, 2, -6))       # перемычка к пластине
    slot = Part.makeBox(3.5, 30, 16, V(-1.75, 14, -8))  # паз к себе (+Y)
    return finalize(fuse_all([p] + pegs + [ring_o, web]).cut(ring_i).cut(slot))
