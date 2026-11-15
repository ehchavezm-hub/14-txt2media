"""Localiza recursos de la aplicación en desarrollo y en el .exe de PyInstaller."""

import sys
from pathlib import Path


def get_recurso(relpath: str) -> Path:
    """Devuelve la ruta absoluta de un recurso.

    En desarrollo: <repo>/recursos/<relpath>
    En PyInstaller (--onedir): sys._MEIPASS/<relpath>
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).parent.parent.parent.parent / "recursos"
    ruta = base / relpath
    return ruta


def get_recurso_existente(relpath: str) -> Path:
    """Como `get_recurso` pero lanza FileNotFoundError si no existe."""
    ruta = get_recurso(relpath)
    if not ruta.exists():
        raise FileNotFoundError(f"Recurso no encontrado: {ruta}")
    return ruta
