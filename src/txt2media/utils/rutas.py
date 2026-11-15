"""Rutas de datos de la aplicación."""

from __future__ import annotations

import os
from pathlib import Path


def get_datos_dir() -> Path:
    """Devuelve el directorio de datos de la app.

    - CONVDOC_DEV=1 → ./datos_dev/ (desarrollo)
    - Windows → %APPDATA%\\txt2media
    - Linux/Mac → ~/.txt2media
    """
    if os.environ.get("CONVDOC_DEV") == "1":
        return Path("datos_dev")

    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "txt2media"

    return Path.home() / ".txt2media"
