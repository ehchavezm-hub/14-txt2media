"""Motor edge-tts — fallback gratuito, requiere Internet."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from txt2media.core.base_voz import ErrorVoz, MotorVoz

_VOZ_DEFAULT = "es-PE-CamilaNeural"


class MotorEdgeTTS(MotorVoz):
    @property
    def nombre(self) -> str:
        return "edge-tts"

    def disponible_en_modo_local(self) -> bool:
        return False

    def disponible(self) -> bool:
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            return False

    def sintetizar(self, texto: str, voz: str, salida: Path) -> None:
        from txt2media.core.modo_local import esta_activo, verificar_red_permitida

        if esta_activo():
            verificar_red_permitida("speech.platform.bing.com")

        try:
            asyncio.run(self._sintetizar_async(texto, voz or _VOZ_DEFAULT, salida))
        except Exception as exc:
            raise ErrorVoz(f"edge-tts falló: {exc}") from exc

    async def _sintetizar_async(self, texto: str, voz: str, salida: Path) -> None:
        import edge_tts

        salida.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(texto, voz)
        await communicate.save(str(salida))
