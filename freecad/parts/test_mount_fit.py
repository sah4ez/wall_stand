# -*- coding: utf-8 -*-
"""Тест крепежа: носики Ø4.4–5.0 и язычки шириной 2.2–2.8.

Печатается первым вместе с test_panel_frag (фрагмент панели с прорезями).
Верхний ряд — голые носики (диаметры по возрастанию слева направо,
число лунок под носиком = диаметр в десятых: 1 лунка = 4.4 ... 4 лунки = 5.0).
Нижний ряд — крючки целиком (носик Ø4.8 + язычок), ширина язычка по
возрастанию (1 лунка = 2.2 ... 4 лунки = 2.8). Подобрав пару, правим
NOSE_D/TONGUE_W в common.py и пересобираем проект.
"""
from common import register, plate, mount_pin, V, finalize
import Part

NOSE_DIA = [4.4, 4.6, 4.8, 5.0]
TONGUE_WS = [2.2, 2.4, 2.6, 2.8]
XS = [-33.0, -11.0, 11.0, 33.0]
MARK_D = 1.25


def _mark(shape, x, z, n):
    """n лунок на лицевой стороне пластины (y=4) для маркировки."""
    for j in range(n):
        dx = (j - (n - 1) / 2.0) * 4.0
        shape = shape.cut(Part.makeCylinder(MARK_D, 2.0,
                                            V(x + dx, 4.0, z), V(0, -1, 0)))
    return shape


@register("test_mount_fit", "Тест крючков: носики 4.4–5.0, язычки 2.2–2.8")
def build():
    shape = Part.makeBox(96.0, 4.0, 64.0, V(-48.0, 0.0, -32.0))
    for i, x in enumerate(XS):
        shape = shape.fuse(Part.makeCylinder(NOSE_DIA[i] / 2.0, 8.0,
                                             V(x, 0, 22.0), V(0, -1, 0)))
        shape = _mark(shape, x, 14.0, i + 1)
        shape = shape.fuse(mount_pin(x, -8.0, NOSE_DIA[2], TONGUE_WS[i]))
        shape = _mark(shape, x, -18.0, i + 1)
    return finalize(shape)


@register("test_panel_frag", "Фрагмент панели: прорези 2.2–2.8 под язычки")
def build():
    """Фрагмент панели с «ключовинами»: круг Ø5.0 + прорезь вниз 9 мм."""
    t = 4.0
    shape = Part.makeBox(96.0, t, 56.0, V(-48.0, 0.0, -34.0))
    for i, x in enumerate(XS):
        w = TONGUE_WS[i] / 2.0
        circle = Part.makeCylinder(2.5, t + 2.0, V(x, -1.0, 0.0), V(0, 1, 0))
        slot = Part.makeBox(w * 2, t + 2.0, 9.0, V(x - w, -1.0, -9.0))
        shape = shape.cut(circle).cut(slot)
        shape = _mark(shape, x, -20.0, i + 1)
    return finalize(shape)
