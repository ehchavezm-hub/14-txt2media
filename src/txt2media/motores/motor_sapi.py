"""Motor SAPI5 vía pyttsx3 — fallback local sin red (solo Windows)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from txt2media.core.base_voz import ErrorVoz, MotorVoz


class MotorSAPI(MotorVoz):
    @property
    def nombre(self) -> str:
        return "sapi"

    def disponible_en_modo_local(self) -> bool:
        return True

    def disponible(self) -> bool:
        if os.name != "nt":
            return False
        try:
            import pyttsx3  # noqa: F401
            return True
        except ImportError:
            return False

    def sintetizar(self, texto: str, voz: str, salida: Path) -> None:
        if os.name != "nt":
            raise ErrorVoz("SAPI solo disponible en Windows")
        try:
            import pyttsx3
        except ImportError as exc:
            raise ErrorVoz("pyttsx3 no instalado") from exc

        salida.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".wav", dir=salida.parent)
        os.close(fd)

        try:
            engine = pyttsx3.init()
            if voz:
                voices = engine.getProperty("voices")
                for v in voices:
                    if voz.lower() in (v.name or "").lower():
                        engine.setProperty("voice", v.id)
                        break
            engine.save_to_file(texto, tmp)
            engine.runAndWait()
            del engine
            # SAPI guarda WAV; renombramos a .wav si la salida pide .mp3
            # El orquestador de audio se encarga de convertir si es necesario
            if salida.suffix.lower() == ".wav":
                os.replace(tmp, salida)
            else:
                os.replace(tmp, salida.with_suffix(".wav"))
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
        except Exception as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise ErrorVoz(f"SAPI error: {exc}") from exc
