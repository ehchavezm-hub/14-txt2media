"""
lanzar.pyw — Doble clic para abrir txt2media (sin ventana de consola).
Funciona en cualquier Windows con Python 3.12+ instalado (32-bit, 64-bit, ARM).
No requiere compilar ningún EXE.
"""
import sys
import os
import runpy

_HERE = os.path.dirname(os.path.abspath(__file__))
# En el ZIP portable src/ está al lado; en el repositorio, dos niveles arriba.
for _base in (_HERE, os.path.dirname(os.path.dirname(_HERE))):
    if os.path.isdir(os.path.join(_base, "src")):
        _HERE = _base
        break
_SRC  = os.path.join(_HERE, "src")

for _p in (_SRC, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

runpy.run_module("txt2media.ui.ventana_principal", run_name="__main__", alter_sys=True)
