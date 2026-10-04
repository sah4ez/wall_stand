# -*- coding: utf-8 -*-
"""Сборка FreeCAD-проекта настенных элементов и экспорт STL/STEP.

Запускается внутри FreeCAD (например, через MCP-инструмент
execute_code_headless сервера freecad-mcp):

    g = {"__file__": "<проект>/freecad/build_all.py", "__name__": "__main__"}
    exec(compile(open(g["__file__"]).read(), g["__file__"], "exec"), g)

Создаёт output/wall_stand_accessories.FCStd, output/stl/*.stl (в печатной
ориентации) и output/step/*.step; печатает таблицу валидации.
"""
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output")
STL_DIR = os.path.join(OUT, "stl")
STEP_DIR = os.path.join(OUT, "step")
DOC_NAME = "wall_stand_accessories"

sys.path.insert(0, HERE)
import common  # noqa: E402
from common import REGISTRY, export_stl  # noqa: E402

# порядок импорта = порядок в документе
PART_FILES = [
    "test_mount_fit",  # регистрирует и test_panel_frag
    "clip_cable",
    "hook_double",
    "headband_holder",
    "small_tray",
    "shelf",
    "basket",
    "cup",
]


def main():
    import FreeCAD as App
    import Import

    for d in (OUT, STL_DIR, STEP_DIR):
        os.makedirs(d, exist_ok=True)

    import importlib
    for mod in PART_FILES:
        importlib.import_module("parts." + mod)

    doc = App.newDocument(DOC_NAME)
    group = doc.addObject("App::DocumentObjectGroup", "Accessories")

    print("VALIDATION name ok solids volume_mm3 bbox_xyz")
    failures = []
    for name, label, fn in REGISTRY:
        try:
            shape = fn()
            ok = shape.isValid()
            n_solids = len(shape.Solids)
            bb = shape.BoundBox
            dims = (bb.XLength, bb.YLength, bb.ZLength)
            fits = max(dims) <= 180.0
            if not (ok and n_solids == 1 and fits and shape.Volume > 0):
                failures.append(name)
            obj = doc.addObject("Part::Feature", name)
            obj.Label = label
            obj.Shape = shape
            group.addObject(obj)

            export_stl(shape, os.path.join(STL_DIR, name + ".stl"))
            Import.export([obj], os.path.join(STEP_DIR, name + ".step"))
            print("VALIDATION %s ok=%s solids=%d vol=%.1f bbox=%.1fx%.1fx%.1f fits=%s"
                  % (name, ok, n_solids, shape.Volume, dims[0], dims[1],
                     dims[2], fits))
        except Exception:
            failures.append(name)
            print("VALIDATION %s FAILED" % name)
            traceback.print_exc()

    doc.saveAs(os.path.join(OUT, DOC_NAME + ".FCStd"))
    print("SAVED %s" % os.path.join(OUT, DOC_NAME + ".FCStd"))
    print("BUILD_RESULT %s" % ("OK" if not failures else "FAILED:" + ",".join(failures)))


main()
