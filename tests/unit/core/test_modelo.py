"""Tests del modelo de datos interno."""

from pathlib import Path

from txt2media.core.modelo import (
    Bloque,
    Documento,
    FilaTabla,
    Imagen,
    NivelResumen,
    Resumen,
    Seccion,
    Tabla,
    TipoBloque,
)


def test_documento_valores_por_defecto() -> None:
    doc = Documento()
    assert doc.titulo == ""
    assert doc.secciones == []
    assert doc.idioma == "es"


def test_documento_con_titulo() -> None:
    doc = Documento(titulo="Informe de Obra", autor="Juan", paginas=50)
    assert doc.titulo == "Informe de Obra"
    assert doc.paginas == 50


def test_bloque_tipo_parrafo() -> None:
    b = Bloque(tipo=TipoBloque.PARRAFO, contenido="Texto de prueba")
    assert b.tipo == TipoBloque.PARRAFO
    assert b.contenido == "Texto de prueba"


def test_bloque_tipo_tabla() -> None:
    tabla = Tabla(
        encabezados=["Col1", "Col2"],
        filas=[FilaTabla(celdas=["A", "B"]), FilaTabla(celdas=["C", "D"])],
        confianza=0.95,
    )
    b = Bloque(tipo=TipoBloque.TABLA, tabla=tabla)
    assert b.tabla is not None
    assert len(b.tabla.filas) == 2


def test_seccion_nivel_y_titulo() -> None:
    s = Seccion(nivel=1, titulo="Introducción", pagina_origen=1)
    assert s.nivel == 1
    assert s.titulo == "Introducción"
    assert s.bloques == []


def test_seccion_agrega_bloque() -> None:
    s = Seccion(nivel=2, titulo="Metodología")
    b = Bloque(tipo=TipoBloque.PARRAFO, contenido="Se usó el método X")
    s.bloques.append(b)
    assert len(s.bloques) == 1


def test_documento_agrega_secciones() -> None:
    doc = Documento(titulo="Test")
    doc.secciones.append(Seccion(nivel=1, titulo="Cap 1"))
    doc.secciones.append(Seccion(nivel=1, titulo="Cap 2"))
    assert len(doc.secciones) == 2


def test_nivel_resumen_enum() -> None:
    assert NivelResumen.BREVE.value == "breve"
    assert NivelResumen.COMPLETO.value == "completo"


def test_imagen_valores_por_defecto() -> None:
    img = Imagen()
    assert img.pie == ""
    assert img.texto_alternativo == ""
    assert img.ruta_temporal is None


def test_resumen_es_original_recortado_por_defecto_false() -> None:
    r = Resumen(texto="Resumen corto", nivel=NivelResumen.BREVE)
    assert r.es_original_recortado is False


def test_documento_secciones_independientes() -> None:
    """Dos documentos no comparten la misma lista de secciones (problema de mutable defaults)."""
    doc1 = Documento()
    doc2 = Documento()
    doc1.secciones.append(Seccion(titulo="S1"))
    assert doc2.secciones == []
