"""Configuración de txt2media. Secretos en keyring, nunca en JSON."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from txt2media.utils.rutas import get_datos_dir

_SERVICIO_KEYRING = "txt2media"


@dataclass
class Configuracion:
    idioma: str = "es-PE"
    voz_predeterminada: str = "es-PE-CamilaNeural"
    azure_region: str = "eastus"
    modo_local: bool = False
    max_chars_fragmento: int = 3000
    cuota_mensual_chars: int = 500_000
    fps_video: int = 24
    segs_por_frame: int = 5
    extra: dict = field(default_factory=dict)

    @classmethod
    def cargar(cls) -> "Configuracion":
        import json
        ruta = get_datos_dir() / "config.json"
        if ruta.exists():
            try:
                data = json.loads(ruta.read_text(encoding="utf-8"))
                campos = {k: v for k, v in data.items() if k != "extra"}
                return cls(**{k: v for k, v in campos.items()
                              if k in cls.__dataclass_fields__})
            except Exception:
                pass
        return cls()

    def guardar(self) -> None:
        import json, os, tempfile
        from dataclasses import asdict
        ruta = get_datos_dir() / "config.json"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        datos = {k: v for k, v in asdict(self).items() if k != "extra"}
        fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=ruta.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            os.replace(tmp, ruta)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise


def guardar_clave(nombre: str, valor: str) -> None:
    """Guarda una clave en el Administrador de credenciales de Windows."""
    try:
        import keyring
        keyring.set_password(_SERVICIO_KEYRING, nombre, valor)
    except Exception:
        pass


def obtener_clave(nombre: str) -> str | None:
    """Obtiene una clave del Administrador de credenciales."""
    try:
        import keyring
        return keyring.get_password(_SERVICIO_KEYRING, nombre)
    except Exception:
        return None
