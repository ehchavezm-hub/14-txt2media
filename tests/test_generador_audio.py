"""Tests del generador de audio y funciones v1.0.1."""
import pytest
from txt2media.generadores.generador_audio import (
    _nombre_capitulo,
    _partir_texto,
    _texto_de_seccion,
)
from txt2media.core.modelo import Bloque, Seccion, TipoBloque


def test_nombre_capitulo_basico():
    nombre = _nombre_capitulo(1, "Introducción")
    assert nombre.startswith("01_")
    assert nombre.endswith(".mp3")


def test_nombre_capitulo_sin_tildes():
    nombre = _nombre_capitulo(3, "Capítulo Tres")
    assert "cap" in nombre.lower()
    assert nombre.endswith(".mp3")


def test_nombre_capitulo_vacio():
    nombre = _nombre_capitulo(5, "")
    assert nombre == "05_capitulo_5.mp3"


def test_nombre_capitulo_indice_doble_digito():
    nombre = _nombre_capitulo(10, "Conclusiones")
    assert nombre.startswith("10_")


def test_texto_de_seccion():
    sec = Seccion(
        titulo="Mi sección",
        nivel=1,
        bloques=[
            Bloque(tipo=TipoBloque.PARRAFO, contenido="Párrafo uno."),
            Bloque(tipo=TipoBloque.LISTA, items_lista=["A", "B"]),
        ],
    )
    texto = _texto_de_seccion(sec)
    assert "Mi sección" in texto
    assert "Párrafo uno." in texto
    assert "A" in texto


def test_partir_texto_corto():
    lineas = _partir_texto("Hola mundo", 20)
    assert lineas == ["Hola mundo"]


def test_partir_texto_largo():
    texto = "Esta es una frase bastante larga que debe partirse en varias líneas"
    lineas = _partir_texto(texto, 20)
    assert len(lineas) > 1
    for linea in lineas:
        assert len(linea) <= 20
