"""Tests del modelo de datos."""
from txt2media.core.modelo import (
    Bloque, Documento, Seccion, TipoBloque,
)


def test_bloque_parrafo():
    b = Bloque(tipo=TipoBloque.PARRAFO, contenido="Hola mundo")
    assert b.contenido == "Hola mundo"
    assert b.tipo == TipoBloque.PARRAFO


def test_seccion_basica():
    sec = Seccion(titulo="Intro", nivel=1, bloques=[])
    assert sec.titulo == "Intro"
    assert sec.nivel == 1
    assert sec.bloques == []


def test_documento_con_secciones():
    secs = [
        Seccion(titulo="Cap 1", nivel=1, bloques=[
            Bloque(tipo=TipoBloque.PARRAFO, contenido="Texto aquí")
        ])
    ]
    doc = Documento(titulo="Mi libro", secciones=secs)
    assert doc.titulo == "Mi libro"
    assert len(doc.secciones) == 1
    assert doc.secciones[0].bloques[0].contenido == "Texto aquí"


def test_bloque_lista():
    b = Bloque(tipo=TipoBloque.LISTA, items_lista=["A", "B", "C"])
    assert b.items_lista == ["A", "B", "C"]
