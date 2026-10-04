# -*- coding: utf-8 -*-
"""Крючок двойной: два V-кармана для кабелей, ключей, лёгких вещей.

Печать стоя, без поддержек: наклонные грани 45° и круче к вертикали.
Пеги 2x2: колонки x=±10 (смежные отверстия, шаг 20), ряды z=±20 (шаг 40).
Профиль кармана: пандус 45° от пластины + горизонтальная площадка z=30
и упорная губка вверх до z=42 (вещь лежит в кармане у губки).
"""
from common import register, plate, mount_pin, prism_x, finalize, fuse_all


@register("hook_double", "Крючок двойной")
def build():
    p = plate(46, -40, 40)
    pegs = [mount_pin(x, z) for x in (-10, 10) for z in (20, -20)]
    profile = [(2, 0), (2, 20), (12, 30), (24, 30),
               (24, 42), (28, 42), (28, 14)]
    ramps = [prism_x(profile, cx - 6, cx + 6) for cx in (-11.0, 11.0)]
    return finalize(fuse_all([p] + pegs + ramps))
