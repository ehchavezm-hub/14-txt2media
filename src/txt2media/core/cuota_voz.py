"""CuotaVoz: límite mensual de caracteres TTS, thread-safe."""

from __future__ import annotations

import os
import tempfile
import threading
from datetime import datetime
from pathlib import Path

from txt2media.utils.rutas import get_datos_dir

_lock = threading.Lock()


class CuotaAgotadaError(Exception):
    pass


class CuotaVoz:
    def __init__(self, limite_mensual: int = 500_000) -> None:
        self._limite = limite_mensual
        self._ruta = get_datos_dir() / "cuota_voz.json"

    def _leer(self) -> dict:
        import json
        if self._ruta.exists():
            try:
                return json.loads(self._ruta.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"mes": "", "usados": 0}

    def _guardar(self, datos: dict) -> None:
        import json
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=self._ruta.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(datos, f)
            os.replace(tmp, self._ruta)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    def verificar_y_consumir(self, n_chars: int) -> None:
        with _lock:
            mes_actual = datetime.now().strftime("%Y-%m")
            datos = self._leer()
            if datos.get("mes") != mes_actual:
                datos = {"mes": mes_actual, "usados": 0}
            usados = datos["usados"]
            if usados + n_chars > self._limite:
                raise CuotaAgotadaError(
                    f"Cuota mensual agotada: {usados}/{self._limite} chars usados"
                )
            datos["usados"] = usados + n_chars
            self._guardar(datos)

    def chars_usados(self) -> int:
        mes_actual = datetime.now().strftime("%Y-%m")
        datos = self._leer()
        if datos.get("mes") != mes_actual:
            return 0
        return datos.get("usados", 0)
