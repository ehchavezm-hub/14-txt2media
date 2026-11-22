"""Diseño de los entregables HTML, Markdown y Word."""

from __future__ import annotations

from pathlib import Path

from txt2media.core.modelo import Bloque, Documento, FilaTabla, Seccion, Tabla, TipoBloque


def _doc() -> Documento:
    return Documento(titulo="Libro de prueba", autor="Autora", secciones=[
        Seccion(1, "Capítulo 1", [Bloque(contenido="Texto con 50 % y la ONU. " * 10),
                                 Bloque(tipo=TipoBloque.CITA, contenido="Una cita"),
                                 Bloque(tipo=TipoBloque.LISTA, items_lista=["uno", "dos"])]),
        Seccion(2, "1.1 Detalle", [Bloque(tipo=TipoBloque.TABLA, tabla=Tabla(
            encabezados=["A", "B|C"], filas=[FilaTabla(["1", "2"])])),
            Bloque(tipo=TipoBloque.CODIGO, contenido="x = 1", idioma_codigo="python"),
            Bloque(tipo=TipoBloque.NOTA_PIE, contenido="1. Nota")]),
        Seccion(1, "Capítulo 2", [Bloque(contenido="# no es un título")]),
    ])


def test_html_tres_modos_claros_sin_modo_oscuro(tmp_path):
    from txt2media.generadores.generador_html import GeneradorHTML
    html = GeneradorHTML().generar(_doc(), tmp_path / "x.html").read_text(encoding="utf-8")
    for modo in ('data-tema="blanco"', 'data-tema="sepia"', 'data-tema="gris"'):
        assert modo in html
    assert "oscuro" not in html
    assert 'id="indice"' in html and 'id="buscar"' in html and 'id="avance"' in html
    assert ">1.1<" in html and "1.1 Detalle" not in html  # número del título no se repite
    assert "&lt;" not in "Libro de prueba"


def test_md_indice_con_anclas_y_tablas_escapadas(tmp_path):
    from txt2media.generadores.generador_md import GeneradorMD
    md = GeneradorMD().generar(_doc(), tmp_path / "x.md").read_text(encoding="utf-8")
    assert md.startswith("---\ntitle: \"Libro de prueba\"")
    assert "- [1 · Capítulo 1](#1--capítulo-1)" in md
    assert "## 1 · Capítulo 1" in md and "### 1.1 · Detalle" in md
    assert "B\\|C" in md
    assert "\\# no es un título" in md
    assert "```python" in md and "> [!NOTE]" in md
    assert "style=" not in md


def test_docx_portada_indice_y_paginas(tmp_path):
    from docx import Document
    from txt2media.generadores.generador_docx import GeneradorDOCX
    ruta = GeneradorDOCX().generar(_doc(), tmp_path / "x.docx", {})
    d = Document(str(ruta))
    texto = "\n".join(p.text for p in d.paragraphs)
    assert "Contenido" in texto and "Capítulo 1" in texto
    assert d.core_properties.title == "Libro de prueba"
    xml = d.element.xml
    assert "TOC" in xml
    pie = d.sections[0].footer._element.xml
    assert "NUMPAGES" in pie
