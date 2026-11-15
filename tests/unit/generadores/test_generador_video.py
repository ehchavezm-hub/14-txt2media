"""Tests para GeneradorVideo — TDD RED primero."""

from __future__ import annotations

import io
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque
from txt2media.generadores.generador_video import GeneradorVideo, _frames_de_documento


def _doc_simple() -> Documento:
    sec1 = Seccion(
        nivel=1,
        titulo="Introducción",
        bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido="Párrafo de prueba.")],
    )
    sec2 = Seccion(
        nivel=1,
        titulo="Conclusión",
        bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido="Fin del documento.")],
    )
    return Documento(titulo="Video Test", secciones=[sec1, sec2])


def _audio_wav_minimo() -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 1600)
    return buf.getvalue()


class TestFramesDeDocumento:
    def test_devuelve_lista_de_imagenes(self):
        doc = _doc_simple()
        frames = _frames_de_documento(doc)
        assert isinstance(frames, list)
        assert len(frames) > 0

    def test_imagenes_son_pil(self):
        doc = _doc_simple()
        frames = _frames_de_documento(doc)
        for f in frames:
            assert isinstance(f, Image.Image)

    def test_dimension_1920x1080(self):
        doc = _doc_simple()
        frames = _frames_de_documento(doc)
        for f in frames:
            assert f.size == (1920, 1080)

    def test_frame_por_seccion_mas_portada(self):
        doc = _doc_simple()  # 2 secciones
        frames = _frames_de_documento(doc)
        # Al menos: portada + 1 frame por sección
        assert len(frames) >= 3

    def test_documento_vacio_genera_portada(self):
        doc = Documento(titulo="Vacío", secciones=[])
        frames = _frames_de_documento(doc)
        assert len(frames) >= 1


class TestGeneradorVideo:
    def test_genera_archivo_mp4(self, tmp_path):
        """Genera un MP4 real usando ffmpeg."""
        audio_bytes = _audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorVideo(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "salida.mp4"
        gen.generar(doc, salida)

        assert salida.exists()
        assert salida.stat().st_size > 0

    def test_archivo_es_mp4_valido(self, tmp_path):
        """El archivo empieza con la firma MP4 (ftyp box o mdat/moov)."""
        audio_bytes = _audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorVideo(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "out.mp4"
        gen.generar(doc, salida)

        data = salida.read_bytes()
        # MP4: bytes 4-8 = "ftyp" o contenedor ISO
        assert b"ftyp" in data[:64] or b"moov" in data or b"mdat" in data

    def test_escritura_atomica(self, tmp_path):
        """No queda .tmp al finalizar."""
        audio_bytes = _audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorVideo(motor=motor_mock)
        doc = _doc_simple()
        gen.generar(doc, tmp_path / "out.mp4")

        tmps = list(tmp_path.glob("*.tmp"))
        assert tmps == []

    def test_genera_srt_si_se_pide(self, tmp_path):
        audio_bytes = _audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorVideo(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "out.mp4"
        gen.generar(doc, salida, generar_srt=True)

        srt = salida.with_suffix(".srt")
        assert srt.exists()
        assert "1\n" in srt.read_text(encoding="utf-8")

    def test_sin_motor_genera_video_silencioso(self, tmp_path):
        """Sin motor de voz se genera video sin pista de audio."""
        gen = GeneradorVideo(motor=None)
        doc = _doc_simple()
        salida = tmp_path / "out.mp4"
        gen.generar(doc, salida)

        assert salida.exists()
        assert salida.stat().st_size > 0

    def test_fps_configurable(self, tmp_path):
        audio_bytes = _audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorVideo(motor=motor_mock, fps=1)
        doc = _doc_simple()
        salida = tmp_path / "out.mp4"
        gen.generar(doc, salida)  # No debe lanzar

        assert salida.exists()
