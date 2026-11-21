"""
lanzar.pyw — Doble clic para abrir txt2media (sin ventana de consola).
Funciona en cualquier Windows con Python 3.12+ instalado (32-bit, 64-bit, ARM).
No requiere compilar ningún EXE.
"""
import sys
import os
import runpy

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.join(_HERE, "src")

for _p in (_SRC, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

runpy.run_module("txt2media.ui.ventana_principal", run_name="__main__", alter_sys=True)
