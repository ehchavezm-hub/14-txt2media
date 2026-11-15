"""Tests del modelo de datos interno."""

from txt2media.core.modelo import (
    Bloque, Documento, FilaTabla, Imagen, Seccion, Tabla, TipoBloque,
)


def test_documento_valores_por_defecto() -> None:
    doc = Documento()
    assert doc.titulo == ""
    assert doc.secciones == []
    assert doc.idioma == "es"


def test_documento_con_titulo() -> None:
    doc = Documento(titulo="Informe de Obra", autor="Juan")
    assert doc.titulo == "Informe de Obra"
    assert doc.autor == "Juan"


def test_bloque_tipo_parrafo() -> None:
    b = Bloque(tipo=TipoBloque.PARRAFO, contenido="Texto de prueba")
    assert b.tipo == TipoBloque.PARRAFO
    assert b.contenido == "Texto de prueba"


def test_bloque_negrita_cursiva() -> None:
    b = Bloque(tipo=TipoBloque.PARRAFO, contenido="bold", negrita=True, cursiva=False)
    assert b.negrita is True
    assert b.cursiva is False


def test_bloque_caption_nota_pie() -> None:
    cap = Bloque(tipo=TipoBloque.CAPTION, contenido="Fig 1.")
    nota = Bloque(tipo=TipoBloque.NOTA_PIE, contenido="1. Fuente.")
    assert cap.tipo == TipoBloque.CAPTION
    assert nota.tipo == TipoBloque.NOTA_PIE


def test_bloque_tipo_tabla() -> None:
    tabla = Tabla(
        encabezados=["Col1", "Col2"],
        filas=[FilaTabla(celdas=["A", "B"]), FilaTabla(celdas=["C", "D"])],
    )
    b = Bloque(tipo=TipoBloque.TABLA, tabla=tabla)
    assert b.tabla is not None
    assert len(b.tabla.filas) == 2


def test_seccion_nivel_y_titulo() -> None:
    s = Seccion(nivel=1, titulo="Introducción")
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


def test_tipo_bloque_enum_completo() -> None:
    tipos = {t.value for t in TipoBloque}
    assert "parrafo" in tipos
    assert "titulo" in tipos
    assert "lista" in tipos
    assert "tabla" in tipos
    assert "caption" in tipos
    assert "nota_pie" in tipos


def test_imagen_valores_por_defecto() -> None:
    img = Imagen()
    assert img.alt == ""
    assert img.ruta is None


def test_documento_secciones_independientes() -> None:
    doc1 = Documento()
    doc2 = Documento()
    doc1.secciones.append(Seccion(titulo="S1"))
    assert doc2.secciones == []
