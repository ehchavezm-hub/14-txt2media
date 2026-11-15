"""Lanzador GUI: usa pythonw -m para evitar consola DOS."""
import sys
import os
import subprocess

# pythonw.exe esta junto a python.exe en la misma carpeta
pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw):
    pythonw = sys.executable  # fallback: usa python normal

# Lanzar como modulo (-m) para que encuentre el paquete instalado
subprocess.Popen([pythonw, "-m", "txt2media.ui.ventana_principal"])
