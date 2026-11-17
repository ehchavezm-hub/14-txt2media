"""
main_exe.py — Punto de entrada para PyInstaller.
El EXE abre txt2media directamente. Sin instalar, sin admin.
"""
from txt2media.ui.ventana_principal import lanzar_app

if __name__ == "__main__":
    lanzar_app()
