"""Tests de generadores PPTX, DOCX y XLSX."""
import pytest
from pathlib import Path
from txt2media.core.modelo import Bloque, Documento, FilaTabla, Seccion, Tabla, TipoBloque


def _doc_simple() -> Documento:
    return Documento(
        titulo="Documento de prueba",
        secciones=[
            Seccion(
                titulo="Capítulo 1",
                nivel=1,
                bloques=[
                    Bloque(tipo=TipoBloque.PARRAFO, contenido="Texto del capítulo uno."),
                    Bloque(tipo=TipoBloque.LISTA, items_lista=["Punto A", "Punto B"]),
                ],
            ),
            Seccion(
                titulo="Datos",
                nivel=2,
                bloques=[
                    Bloque(
                        tipo=TipoBloque.TABLA,
                        tabla=Tabla(
                            encabezados=["Nombre", "Valor"],
                            filas=[FilaTabla(celdas=["Alpha", "1"]), FilaTabla(celdas=["Beta", "2"])],
                        ),
                    )
                ],
            ),
        ],
    )


def test_generar_pptx(tmp_path):
    from txt2media.generadores.generador_pptx import GeneradorPPTX

    salida = tmp_path / "out.pptx"
    GeneradorPPTX().generar(_doc_simple(), salida, {})
    assert salida.exists()
    assert salida.stat().st_size > 0


def test_generar_docx(tmp_path):
    from txt2media.generadores.generador_docx import GeneradorDOCX

    salida = tmp_path / "out.docx"
    GeneradorDOCX().generar(_doc_simple(), salida, {})
    assert salida.exists()
    assert salida.stat().st_size > 0


def test_generar_xlsx(tmp_path):
    from txt2media.generadores.generador_xlsx import GeneradorXLSX

    salida = tmp_path / "out.xlsx"
    GeneradorXLSX().generar(_doc_simple(), salida, {})
    assert salida.exists()
    assert salida.stat().st_size > 0


def test_pptx_escribe_atomicamente(tmp_path):
    from txt2media.generadores.generador_pptx import GeneradorPPTX

    salida = tmp_path / "atomic.pptx"
    GeneradorPPTX().generar(_doc_simple(), salida, {})
    # Solo debe existir el archivo final, no temporales
    tmps = list(tmp_path.glob("*.tmp"))
    assert len(tmps) == 0
