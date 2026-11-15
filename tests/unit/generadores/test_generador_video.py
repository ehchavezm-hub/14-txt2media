"""Tests para GeneradorVideo."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque
from txt2media.generadores.generador_video import GeneradorVideo


def _doc_simple() -> Documento:
    return Documento(
        titulo="Video Test",
        secciones=[
            Seccion(nivel=1, titulo="Introducción", bloques=[
                Bloque(tipo=TipoBloque.PARRAFO, contenido="Párrafo de prueba."),
            ]),
            Seccion(nivel=1, titulo="Conclusión", bloques=[
                Bloque(tipo=TipoBloque.PARRAFO, contenido="Fin del documento."),
            ]),
        ]
    )


def test_generador_video_instancia() -> None:
    gen = GeneradorVideo(voz="es-PE-CamilaNeural")
    assert gen is not None


def test_generador_video_metodo_generar() -> None:
    gen = GeneradorVideo(voz="es-PE-CamilaNeural")
    assert callable(gen.generar)


@pytest.mark.skipif(True, reason="Requiere ffmpeg y edge-tts en modo integración")
def test_generar_video_produce_mp4(tmp_path) -> None:
    gen = GeneradorVideo(voz="es-PE-CamilaNeural")
    salida = tmp_path / "out.mp4"
    gen.generar(_doc_simple(), salida)
    assert salida.exists()
    assert salida.stat().st_size > 0
