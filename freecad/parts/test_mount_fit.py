# -*- coding: utf-8 -*-
"""Тест крепежа: брусья 4.8–5.4 и защёлки 3.6–4.2 + фрагмент панели.

Печатается первым вместе с test_panel_frag. Верхний ряд — голые брусья
(в застёгнутом положении, как на крючках), нижний — крючки целиком
(брус + наклонная защёлка). Число лунок-маркеров = размер в десятых:
1 лунка -> 4.8/3.6, ... 4 лунки -> 5.4/4.2. Подобрав пару, правим
HOOK_W/TAB_T в common.py и пересобираем проект.
"""
from common import register, mount_pin, V, finalize
import Part

PLUG_WS = [4.8, 5.0, 5.2, 5.4]
TAB_TS = [3.6, 3.8, 4.0, 4.2]
XS = [-33.0, -11.0, 11.0, 33.0]
MARK_D = 1.25


def _mark(shape, x, z, n):
    """n лунок на лицевой стороне пластины (y=4) для маркировки."""
    for j in range(n):
        dx = (j - (n - 1) / 2.0) * 4.0
        shape = shape.cut(Part.makeCylinder(MARK_D, 2.0,
                                            V(x + dx, 4.0, z), V(0, -1, 0)))
    return shape


@register("test_mount_fit", "Тест крючков: брусья 4.8–5.4, защёлки 3.6–4.2")
def build():
    shape = Part.makeBox(96.0, 4.0, 64.0, V(-48.0, 0.0, -32.0))
    for i, x in enumerate(XS):
        w = PLUG_WS[i]
        shape = shape.fuse(Part.makeBox(w, 7.0, 5.0,
                                        V(x - w / 2.0, -7.0, 19.5)))
        shape = _mark(shape, x, 12.0, i + 1)
        shape = shape.fuse(mount_pin(x, -8.0, w, TAB_TS[i]))
        shape = _mark(shape, x, -28.0, i + 1)
    return finalize(shape)


def _slot(x, w, h, r, t):
    """Вертикальная прорезь w x h со скруглениями r, глубиной t вдоль +Y."""
    import Part as P
    parts = [
        P.makeBox(w, t, h - 2 * r, V(x - w / 2.0, -1.0, -h / 2.0 + r)),
        P.makeBox(w - 2 * r, t, h, V(x - w / 2.0 + r, -1.0, -h / 2.0)),
    ]
    for sx in (-1, 1):
        for sz in (-1, 1):
            parts.append(P.makeCylinder(
                r, t, V(x + sx * (w / 2.0 - r), -1.0, sz * (h / 2.0 - r)),
                V(0, 0, 1)))
    out = parts[0]
    for s in parts[1:]:
        out = out.fuse(s)
    return out


@register("test_panel_frag", "Фрагмент панели: прорези 5.4–5.8 x 15, R2")
def build():
    """Фрагмент панели 4.5 мм с вертикальными прорезями (R2)."""
    t = 4.5
    shape = Part.makeBox(96.0, t, 50.0, V(-48.0, 0.0, -30.0))
    slot_ws = [5.4, 5.5, 5.6, 5.8]
    for i, x in enumerate(XS):
        shape = shape.cut(_slot(x, slot_ws[i], 15.0, 2.0, t + 2.0))
        shape = _mark(shape, x, -18.0, i + 1)
    return finalize(shape)
