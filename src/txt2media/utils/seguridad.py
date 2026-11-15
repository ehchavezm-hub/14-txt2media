"""Validación de seguridad para archivos ZIP y XML externos."""

import zipfile
from pathlib import Path


class RutaMaliciosaError(ValueError):
    """El ZIP contiene rutas que intentan salir del directorio de extracción."""


class ZipBombaError(ValueError):
    """El ZIP supera el límite de tamaño descomprimido."""


def validar_zip(
    ruta: Path,
    max_bytes: int = 20_971_520,  # 20 MB por defecto
    extensiones_permitidas: frozenset[str] | None = None,
) -> None:
    """Valida que un archivo ZIP es seguro antes de extraerlo.

    Lanza:
        RutaMaliciosaError: si alguna entrada tiene ruta con ".." o raíz absoluta.
        ZipBombaError: si el tamaño total descomprimido supera max_bytes.
        zipfile.BadZipFile: si el archivo no es un ZIP válido.
    """
    with zipfile.ZipFile(ruta, "r") as zf:
        total_size = 0
        for info in zf.infolist():
            # Detectar rutas maliciosas
            nombre = info.filename
            partes = Path(nombre).parts
            if ".." in partes or (partes and partes[0].startswith("/")):
                raise RutaMaliciosaError(
                    f"Ruta maliciosa en ZIP: '{nombre}'"
                )
            # Verificar extensiones si se especifican
            if extensiones_permitidas is not None:
                sufijo = Path(nombre).suffix.lower()
                if sufijo and sufijo not in extensiones_permitidas:
                    raise RutaMaliciosaError(
                        f"Tipo de archivo no permitido en ZIP: '{nombre}'"
                    )
            # Acumular tamaño
            total_size += info.file_size
            if total_size > max_bytes:
                raise ZipBombaError(
                    f"ZIP supera el límite de {max_bytes:,} bytes descomprimidos"
                )
