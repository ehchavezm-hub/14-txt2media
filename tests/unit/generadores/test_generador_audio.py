"""Tests para GeneradorAudio — TDD RED primero."""

from __future__ import annotations

import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque
from txt2media.generadores.generador_audio import (
    GeneradorAudio,
    _nombre_capitulo,
    _texto_de_documento,
    _texto_de_seccion,
)


def _doc_simple() -> Documento:
    """Documento de prueba con dos secciones."""
    sec1 = Seccion(
        nivel=1,
        titulo="Introducción",
        bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido="Este es el primer párrafo.")],
    )
    sec2 = Seccion(
        nivel=1,
        titulo="Conclusión",
        bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido="Párrafo final del documento.")],
    )
    return Documento(titulo="Informe Test", secciones=[sec1, sec2])


def _doc_vacio() -> Documento:
    return Documento(titulo="Vacío", secciones=[])


class TestTextoDeDocumento:
    def test_incluye_titulo_documento(self):
        doc = _doc_simple()
        texto = _texto_de_documento(doc)
        assert "Informe Test" in texto

    def test_incluye_titulo_secciones(self):
        doc = _doc_simple()
        texto = _texto_de_documento(doc)
        assert "Introducción" in texto
        assert "Conclusión" in texto

    def test_incluye_parrafos(self):
        doc = _doc_simple()
        texto = _texto_de_documento(doc)
        assert "primer párrafo" in texto

    def test_documento_vacio_devuelve_titulo(self):
        doc = _doc_vacio()
        texto = _texto_de_documento(doc)
        assert "Vacío" in texto

    def test_salida_es_string(self):
        doc = _doc_simple()
        assert isinstance(_texto_de_documento(doc), str)


class TestTextoDeSecccion:
    def test_incluye_titulo_seccion(self):
        sec = Seccion(nivel=1, titulo="Mi sección",
                      bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido="Texto.")])
        assert "Mi sección" in _texto_de_seccion(sec)

    def test_incluye_parrafo(self):
        sec = Seccion(nivel=1, titulo="T",
                      bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido="Contenido importante.")])
        assert "Contenido importante" in _texto_de_seccion(sec)

    def test_seccion_vacia_devuelve_vacio(self):
        sec = Seccion(nivel=1, titulo="", bloques=[])
        assert _texto_de_seccion(sec).strip() == ""


class TestNombreCapitulo:
    def test_formato_numerado(self):
        assert _nombre_capitulo(1, "Introducción").startswith("01_")

    def test_extiension_mp3(self):
        assert _nombre_capitulo(1, "Cap").endswith(".mp3")

    def test_numero_dos_digitos(self):
        assert _nombre_capitulo(9, "Cap").startswith("09_")

    def test_limpia_caracteres_especiales(self):
        nombre = _nombre_capitulo(1, "Cap: ¿Qué?")
        assert "?" not in nombre
        assert "¿" not in nombre


class TestGeneradorAudio:
    def _audio_wav_minimo(self) -> bytes:
        """Genera bytes de un WAV válido de 0.1s."""
        import io, struct
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"\x00\x00" * 1600)
        return buf.getvalue()

    def test_genera_archivo_wav(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "salida.wav"
        gen.generar(doc, salida)

        assert salida.exists()
        assert salida.stat().st_size > 0

    def test_genera_archivo_mp3(self, tmp_path):
        """Si ffmpeg no está disponible, acepta MP3 como WAV con extensión diferente."""
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "salida.mp3"
        gen.generar(doc, salida)

        assert salida.exists()

    def test_llama_al_motor_con_texto(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        gen.generar(doc, tmp_path / "out.wav")

        assert motor_mock.sintetizar.called

    def test_escritura_atomica(self, tmp_path):
        """El archivo destino aparece completo (no existe archivo .tmp al finalizar)."""
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "out.wav"
        gen.generar(doc, salida)

        # No debe quedar ningún .tmp en tmp_path
        tmps = list(tmp_path.glob("*.tmp"))
        assert tmps == []

    def test_genera_srt_si_se_pide(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "out.wav"
        gen.generar(doc, salida, generar_srt=True)

        srt = salida.with_suffix(".srt")
        assert srt.exists()
        contenido = srt.read_text(encoding="utf-8")
        assert "1\n" in contenido  # Al menos una entrada SRT

    def test_srt_formato_correcto(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        salida = tmp_path / "out.wav"
        gen.generar(doc, salida, generar_srt=True)

        srt = salida.with_suffix(".srt")
        lineas = srt.read_text(encoding="utf-8").splitlines()
        # Primera entrada: número, tiempo, texto
        assert lineas[0] == "1"
        assert "-->" in lineas[1]

    def test_voz_por_defecto_espanol(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        gen.generar(doc, tmp_path / "out.wav")

        args = motor_mock.sintetizar.call_args
        voz = args[0][1] if args[0] else args[1].get("voz", "")
        assert "es" in voz.lower() or voz == ""

    def test_voz_por_defecto_es_camila_pe(self, tmp_path):
        """La voz predeterminada debe ser es-PE-CamilaNeural."""
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        gen.generar(doc, tmp_path / "out.wav")

        args = motor_mock.sintetizar.call_args
        voz = args[0][1] if args[0] else args[1].get("voz", "")
        assert voz == "es-PE-CamilaNeural"

    def test_generar_capitulos_crea_carpeta(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        carpeta = tmp_path / "capitulos"
        gen.generar_capitulos(doc, carpeta)

        assert carpeta.exists()

    def test_generar_capitulos_un_archivo_por_seccion(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()  # 2 secciones
        carpeta = tmp_path / "caps"
        archivos = gen.generar_capitulos(doc, carpeta)

        assert len(archivos) == 2

    def test_generar_capitulos_nombres_numerados(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        carpeta = tmp_path / "caps"
        archivos = gen.generar_capitulos(doc, carpeta)

        nombres = [a.name for a in archivos]
        assert nombres[0].startswith("01_")
        assert nombres[1].startswith("02_")

    def test_generar_capitulos_crea_playlist(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        carpeta = tmp_path / "caps"
        gen.generar_capitulos(doc, carpeta)

        assert (carpeta / "playlist.m3u").exists()
        contenido = (carpeta / "playlist.m3u").read_text(encoding="utf-8")
        assert "#EXTM3U" in contenido
        assert "Introducción" in contenido

    def test_generar_capitulos_crea_cover(self, tmp_path):
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        gen = GeneradorAudio(motor=motor_mock)
        doc = _doc_simple()
        carpeta = tmp_path / "caps"
        gen.generar_capitulos(doc, carpeta)

        assert (carpeta / "cover.jpg").exists()

    def test_fragmenta_texto_largo(self, tmp_path):
        """Texto > 3000 chars debe llamar al motor más de una vez."""
        audio_bytes = self._audio_wav_minimo()
        motor_mock = MagicMock()
        motor_mock.sintetizar.return_value = audio_bytes

        # Documento con texto muy largo
        texto_largo = "palabra " * 500  # ~4000 chars
        sec = Seccion(
            nivel=1,
            titulo="Sección larga",
            bloques=[Bloque(tipo=TipoBloque.PARRAFO, contenido=texto_largo)],
        )
        doc = Documento(titulo="Doc largo", secciones=[sec])

        gen = GeneradorAudio(motor=motor_mock, max_chars_fragmento=500)
        gen.generar(doc, tmp_path / "out.wav")

        assert motor_mock.sintetizar.call_count > 1
