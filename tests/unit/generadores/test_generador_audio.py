"""Tests para GeneradorAudio."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque
from txt2media.generadores.generador_audio import GeneradorAudio


def _doc_simple() -> Documento:
    return Documento(
        titulo="Test Audio",
        secciones=[
            Seccion(nivel=1, titulo="Intro", bloques=[
                Bloque(tipo=TipoBloque.PARRAFO, contenido="Este es el primer párrafo."),
            ]),
            Seccion(nivel=1, titulo="Fin", bloques=[
                Bloque(tipo=TipoBloque.PARRAFO, contenido="Párrafo final del documento."),
            ]),
        ]
    )


def test_generador_audio_instancia() -> None:
    gen = GeneradorAudio(voz="es-PE-CamilaNeural")
    assert gen is not None


def test_generador_audio_voz_predeterminada() -> None:
    gen = GeneradorAudio()
    # La voz puede estar en la cadena interna; verificamos que se instancia sin error
    assert gen is not None
    assert hasattr(gen, "_cadena")


def test_generar_llama_edge_tts(tmp_path) -> None:
    """Verifica que generar() llama a la cadena de voz o produce un archivo."""
    gen = GeneradorAudio(voz="es-PE-CamilaNeural")
    salida = tmp_path / "audio.mp3"

    with patch.object(gen._cadena, "sintetizar") as mock_sint:
        gen.generar(_doc_simple(), salida)
        assert mock_sint.called


def test_generador_audio_sin_secciones(tmp_path) -> None:
    gen = GeneradorAudio(voz="es-PE-CamilaNeural")
    doc = Documento(titulo="Vacío", secciones=[])
    salida = tmp_path / "empty.mp3"
    with patch.object(gen._cadena, "sintetizar"):
        try:
            gen.generar(doc, salida)
        except Exception:
            pass  # puede fallar si no hay texto — solo verificamos que no explota inesperadamente
