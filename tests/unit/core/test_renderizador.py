"""Tests para RenderizadorDiapositiva."""

import pytest
from pathlib import Path
from txt2media.core.renderizador import RenderizadorDiapositiva
from txt2media.core.modelo import Seccion, Bloque, TipoBloque


def test_renderizador_dimensiones() -> None:
    r = RenderizadorDiapositiva()
    assert r.ANCHO > 0
    assert r.ALTO > 0


def test_render_portada_devuelve_imagen() -> None:
    from PIL import Image
    r = RenderizadorDiapositiva()
    img = r.render_portada("Test título")
    assert isinstance(img, Image.Image)
    assert img.width == r.ANCHO
    assert img.height == r.ALTO


def test_render_seccion_devuelve_imagen() -> None:
    from PIL import Image
    r = RenderizadorDiapositiva()
    sec = Seccion(nivel=1, titulo="Sección de prueba", bloques=[
        Bloque(tipo=TipoBloque.PARRAFO, contenido="Contenido de prueba.")
    ])
    img = r.render_seccion(sec)
    assert isinstance(img, Image.Image)
