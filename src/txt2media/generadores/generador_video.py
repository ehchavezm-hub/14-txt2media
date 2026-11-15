"""Generador de video: diapositivas PNG + audio → MP4 vía ffmpeg."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from txt2media.core.modelo import Documento

_log = logging.getLogger("txt2media.generador_video")
_DURACION_DIAPOSITIVA = 5  # segundos por diapositiva sin audio


class GeneradorVideo:
    def __init__(self, voz: str = "es-PE-CamilaNeural") -> None:
        self._voz = voz

    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise EnvironmentError(
                "ffmpeg no encontrado. Instálalo y agrega al PATH."
            )

        salida.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            imagenes = self._generar_imagenes(doc, tmp)
            audio = self._generar_audio(doc, tmp)
            self._combinar(imagenes, audio, salida, ffmpeg, tmp)

        return salida

    def _generar_imagenes(self, doc: Documento, tmp: Path) -> list[Path]:
        from txt2media.core.renderizador import RenderizadorDiapositiva

        renderer = RenderizadorDiapositiva()
        imagenes: list[Path] = []

        portada = renderer.render_portada(doc.titulo)
        ruta_portada = tmp / "slide_000.png"
        portada.save(str(ruta_portada))
        imagenes.append(ruta_portada)

        for i, sec in enumerate(doc.secciones, start=1):
            img = renderer.render_seccion(sec)
            ruta = tmp / f"slide_{i:03d}.png"
            img.save(str(ruta))
            imagenes.append(ruta)

        return imagenes

    def _generar_audio(self, doc: Documento, tmp: Path) -> Path | None:
        from txt2media.generadores.generador_audio import GeneradorAudio

        gen = GeneradorAudio(voz=self._voz)
        audio_path = tmp / "naracion.mp3"
        try:
            gen.generar(doc, audio_path)
            return audio_path
        except Exception as exc:
            _log.warning("No se pudo generar audio para video: %s", exc)
            return None

    def _combinar(
        self,
        imagenes: list[Path],
        audio: Path | None,
        salida: Path,
        ffmpeg: str,
        tmp: Path,
    ) -> None:
        lista_txt = tmp / "frames.txt"
        with lista_txt.open("w", encoding="utf-8") as f:
            for img in imagenes:
                f.write(f"file '{img}'\n")
                f.write(f"duration {_DURACION_DIAPOSITIVA}\n")
            if imagenes:
                f.write(f"file '{imagenes[-1]}'\n")

        try:
            cmd = [
                ffmpeg, "-y",
                "-f", "concat", "-safe", "0", "-i", str(lista_txt),
            ]
            if audio and audio.exists():
                cmd += ["-i", str(audio), "-shortest"]
            cmd += [
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "24",
                "-crf", "23",
            ]
            if audio and audio.exists():
                cmd += ["-c:a", "aac", "-b:a", "128k"]
            cmd.append(str(salida))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"ffmpeg error (código {result.returncode}):\n{result.stderr[-500:]}"
                )
        except Exception:
            raise
