# -*- coding: utf-8 -*-
"""Функциональная проверка сохранённого проекта: зондирование точек.

Открывает output/wall_stand_accessories.FCStd и для каждой контрольной
точки проверяет принадлежность телу (isInside). Ловит инвертированные
вырезы, «съеденные» опоры, закрытые полости и т.п.
"""
import os
import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FCSTD = os.path.join(ROOT, "output", "wall_stand_accessories.FCStd")

# (деталь, точка (x,y,z), ожидается внутри?)
PROBES = [
    # --- test_mount_fit ---
    ("test_mount_fit", (33, -4, 22), True),    # носик 5.0
    ("test_mount_fit", (-33, -4, 22), True),   # носик 4.4
    ("test_mount_fit", (-33, -8, -13), True),  # язычок 2.2
    ("test_mount_fit", (33, -8, -13), True),   # язычок 2.8
    ("test_mount_fit", (0, -8, -13), False),   # между язычками пусто
    ("test_mount_fit", (-13, 3, 14), False),   # лунка-маркер
    # --- test_panel_frag ---
    ("test_panel_frag", (40, 2, 20), True),    # тело фрагмента
    ("test_panel_frag", (0, 2, 0), True),      # между ключовинами материал
    ("test_panel_frag", (11, 2, 0), False),    # круг ключовины 2.6
    ("test_panel_frag", (11, 2, -5), False),   # прорезь 2.6
    ("test_panel_frag", (-33, 2, -5), False),  # прорезь 2.2
    ("test_panel_frag", (11, 2, -12), True),   # под прорезью материал
    # --- clip_cable ---
    ("clip_cable", (0, 22, 0), False),         # паз под кабель открыт
    ("clip_cable", (0, 16, 0), False),         # отверстие кольца
    ("clip_cable", (3, 22.5, 0), True),        # стенка кольца
    ("clip_cable", (-10, -8, -5), True),       # язычок крючка
    # --- hook_double ---
    ("hook_double", (11, 18, 25), True),       # тело пандуса
    ("hook_double", (11, 18, 33), False),      # карман над площадкой
    ("hook_double", (11, 26, 36), True),       # упорная губка
    ("hook_double", (-10, -8, -25), True),     # язычок нижнего крючка
    # --- headband_holder ---
    ("headband_holder", (0, 20, 28), True),    # площадка
    ("headband_holder", (0, 20, 36), False),   # над площадкой открыто
    ("headband_holder", (0, 41, 36), True),    # губка
    ("headband_holder", (-20, -8, -25), True), # язычок
    # --- small_tray ---
    ("small_tray", (0, 30, 20), False),        # полость лотка
    ("small_tray", (28.8, 30, 20), True),      # боковая стенка
    ("small_tray", (7, 30, 1.2), True),        # дно между отверстиями
    ("small_tray", (0, 14, 1.2), False),       # отверстие дна
    ("small_tray", (-10, -8, -15), True),      # язычок
    # --- shelf ---
    ("shelf", (0, 40, 16), True),              # плита полки
    ("shelf", (0, 40, 25), False),             # над полкой открыто
    ("shelf", (0, 10, -10), True),             # ребро
    ("shelf", (-40, -8, -25), True),           # язычок
    # --- basket ---
    ("basket", (0, 30, 30), False),            # полость корзины
    ("basket", (58.8, 30, 30), True),          # боковая стенка
    ("basket", (0, 14, 1.2), False),           # отверстие дна
    ("basket", (20, -8, -10), True),           # язычок
    # --- cup ---
    ("cup", (0, 37, 50), False),               # полость стакана
    ("cup", (0, 71.8, 50), True),              # стенка
    ("cup", (10, 3.2, 50), True),              # хорда сплавления с пластиной
    ("cup", (-10, -8, 34), True),              # язычок нижнего крючка
]


def main():
    if App.ActiveDocument:
        App.closeDocument(App.ActiveDocument.Name)
    doc = App.openDocument(FCSTD)
    shapes = {o.Name: o.Shape for o in doc.Objects if hasattr(o, "Shape")}
    fails = 0
    print("PROBE part point expected->actual")
    for name, pt, expect in PROBES:
        v = App.Vector(*[float(c) for c in pt])
        actual = shapes[name].isInside(v, 1e-6, True)
        ok = actual == expect
        fails += 0 if ok else 1
        print("PROBE %s %s want_in=%s got_in=%s %s"
              % (name, pt, expect, actual, "PASS" if ok else "FAIL"))
    print("QA_RESULT %s" % ("OK" if fails == 0 else "FAILED:%d" % fails))


main()
