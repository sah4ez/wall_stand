# -*- coding: utf-8 -*-
"""Общие параметры и построители для настенных элементов (аналог SKÅDIS).

Система координат (эксплуатационная):
  * панель лежит в плоскости Y=0, лицевой стороной к +Y;
  * элемент выступает от панели в +Y, Z — вверх, X — вправо;
  * крючки-защёлки (носик + язычок) уходят в -Y, в отверстия панели,
    и защёлкиваются сдвигом вниз (см. mount_pin).

Все детали печатаются «стоя» в эксплуатационной ориентации
(плоскость Z=0 — стол принтера); язычки крючков — самонесущие стенки
с наклоном круче 45°, печать без поддержек.
"""
import FreeCAD as App
import Part
import MeshPart

# --- Панель 28x28 см: 14 отверстий по горизонтали, 7 по вертикали ---------
HOLE_D = 5.0     # диаметр отверстия панели, мм (SKÅDIS-совместимые панели)
PITCH_X = 20.0   # шаг отверстий по горизонтали, мм (280 / 14)
PITCH_Y = 40.0   # шаг отверстий по вертикали, мм  (280 / 7)

# --- Крючок-защёлка (носик + язычок), интерфейс SKÅDIS-совместимых панелей --
# Отверстие панели — «ключовина»: круг Ø5 с прорезью (~2.6-3 мм) ВНИЗ.
# Установка: носики в круги, сдвиг держателя вниз на ~8 мм — язычки
# заходят в прорези за панель, носик шире прорези и гравитация запирает узел.
NOSE_D = 4.8     # диаметр носика (подбор по тесту: 4.4–5.0)
NOSE_L = 8.0     # длина носика (панель ~4 мм + зазор для язычка)
TONGUE_W = 2.4   # толщина язычка по X (в прорезь)
TONGUE_EMBED = 1.2   # заход язычка в носик по Z для сплавления
TONGUE_OVERLAP = 4.5  # заход язычка в носик по Y (объёмное сплавление)
TONGUE_LEN = 8.0 # длина язычка вниз (ход защёлкивания)

# --- Общие толщины ---------------------------------------------------------
PLATE_T = 4.0    # монтажная пластина
WALL = 2.4       # стенки коробов
BOTTOM = 2.4     # днища коробов
CHAMFER = 2.0    # фаска вертикальных рёбер пластин

EPS = 1e-6


def V(x, y, z):
    return App.Vector(float(x), float(y), float(z))


def mount_pin(x, z, d=NOSE_D, tongue_w=TONGUE_W, length=NOSE_L,
              tongue_len=TONGUE_LEN):
    """Крючок-защёлка: носик (цилиндр по -Y) + треугольный язычок вниз-назад.

    Язычок — самонесущая стенка (гипотенуза круче 45° от горизонтали),
    при защёлкивании ложится в прорезь панели и упирается в её нижний
    торец лёгким клином.
    """
    r = d / 2.0
    nose = Part.makeCylinder(r, length, V(x, 0, z), V(0, -1, 0))
    z_t = z - r + TONGUE_EMBED              # верхняя кромка язычка (в носике)
    y0 = -(length - TONGUE_OVERLAP)         # передняя кромка (внутри носика)
    y1 = -float(length + TONGUE_W)          # задняя кромка (за панелью)
    prof = [(y0, z_t), (y1, z_t), (y1, z_t - tongue_len)]
    tongue = prism_x(prof, x - tongue_w / 2.0, x + tongue_w / 2.0)
    return nose.fuse(tongue)


def plate(w, zmin, zmax, t=PLATE_T, y0=0.0, chamfer=CHAMFER):
    """Монтажная пластина шириной w по X, толщиной t по Y, zmin..zmax по Z."""
    b = Part.makeBox(w, t, zmax - zmin, V(-w / 2.0, y0, zmin))
    if chamfer > 0:
        edges = []
        for e in b.Edges:
            vs = e.Vertexes
            if len(vs) != 2:
                continue
            a, c = vs[0], vs[1]
            if (abs(a.X - c.X) < EPS and abs(a.Z - c.Z) < EPS
                    and abs(abs(a.Y - c.Y) - t) < EPS
                    and abs(abs(a.X) - w / 2.0) < EPS
                    and (abs(a.Z - zmin) < EPS or abs(a.Z - zmax) < EPS)):
                edges.append(e)
        if len(edges) == 4:
            b = b.makeChamfer(chamfer, edges)
    return b


def prism_x(pts, x0, x1):
    """Призма: замкнутый профиль в плоскости YZ (список пар (y, z)),
    выдавленный вдоль X от x0 до x1."""
    pts3 = [V(x0, y, z) for (y, z) in pts]
    pts3.append(pts3[0])
    return Part.Face(Part.makePolygon(pts3)).extrude(V(x1 - x0, 0, 0))


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out


def finalize(shape):
    try:
        shape = shape.removeSplitter()
    except Exception:
        pass
    return shape


REGISTRY = []


def register(name, label):
    def deco(fn):
        REGISTRY.append((name, label, fn))
        return fn
    return deco


def export_stl(shape, path):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05,
                                  AngularDeflection=0.35, Relative=False)
    mesh.write(path)
    return mesh
