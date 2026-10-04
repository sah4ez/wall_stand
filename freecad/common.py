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

# --- Крючок из двух параллелепипедов --------------------------------------
# Прорезь панели: 5.5 (X) x 15 (Z), скругления R2, толщина панели 4.5.
# Брус проходит в прорезь и в застёгнутом виде ложится на её нижнюю кромку;
# наклонная защёлка за панелью не даёт детали откинуться. Снятие — поднять
# на ~6 мм и оттянуть.
SLOT_W = 5.5     # ширина прорези по X
SLOT_H = 15.0    # высота прорези по Z
SLOT_R = 2.0     # скругление углов прорези
PANEL_T = 4.5    # толщина панели
HOOK_W = 5.0     # ширина бруса и защёлки по X (в прорезь 5.5)
PLUG_L = 7.0     # длина бруса по Y (панель 4.5 + зазор 2.5)
PLUG_H = 5.0     # высота бруса по Z
LOCK_DROP = 5.0  # застёгнуто: брус опущен на 5 мм от центра прорези
TAB_T = 4.0      # толщина защёлки (по Y)
TAB_L = 8.0      # длина защёлки (наклон 70° от горизонтали)

# --- Общие толщины ---------------------------------------------------------
PLATE_T = 4.0    # монтажная пластина
WALL = 2.4       # стенки коробов
BOTTOM = 2.4     # днища коробов
CHAMFER = 2.0    # фаска вертикальных рёбер пластин

EPS = 1e-6


def V(x, y, z):
    return App.Vector(float(x), float(y), float(z))


def mount_pin(x, z, w=HOOK_W, tab_t=TAB_T):
    """Крючок из двух параллелепипедов, модель в застёгнутом положении.

    Брус: w x PLUG_L x PLUG_H, проходит в прорезь (5.5 широкой), снизу
    опирается на её нижнюю кромку. Защёлка: w x TAB_T x TAB_L, наклонена
    на 70° к горизонтали вниз-назад от нижне-заднего угла бруса; её нижняя
    часть остаётся за задней стенкой панели и не даёт детали откинуться.
    Обе детали печатаются без поддержек (наклон 70°, низ бруса — мостик
    ~7 мм над защёлкой).
    """
    import math
    c = z - LOCK_DROP                        # центр бруса в застёгнутом виде
    plug = Part.makeBox(w, PLUG_L, PLUG_H, V(x - w / 2.0, -PLUG_L, c - PLUG_H / 2.0))
    ang = math.radians(70.0)
    d = (-math.cos(ang), -math.sin(ang))     # вдоль защёлки (вниз-назад)
    p = (math.sin(ang), -math.cos(ang))      # толщина защёлки
    y0 = -(PLUG_L - 1.2)                     # верх защёлки — внутри бруса
    z0 = c + PLUG_H / 2.0 - 2.0
    A = (y0, z0)
    B = (y0 + TAB_L * d[0], z0 + TAB_L * d[1])
    C = (B[0] + tab_t * p[0], B[1] + tab_t * p[1])
    D = (A[0] + tab_t * p[0], A[1] + tab_t * p[1])
    tab = prism_x([A, B, C, D], x - w / 2.0, x + w / 2.0)
    return plug.fuse(tab)


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
