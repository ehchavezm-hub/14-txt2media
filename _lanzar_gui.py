"""Lanzador intermedio: encuentra pythonw.exe y abre la GUI sin consola."""
import sys
import os
import subprocess

here = os.path.dirname(os.path.abspath(__file__))
pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw):
    pythonw = sys.executable

script = os.path.join(here, "src", "txt2media", "ui", "ventana_principal.py")
subprocess.Popen([pythonw, script])
