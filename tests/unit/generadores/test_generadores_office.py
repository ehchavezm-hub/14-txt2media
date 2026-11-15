"""Tests para generadores DOCX, XLSX y PPTX."""

import pytest
from pathlib import Path

from txt2media.core.modelo import (
    Bloque, Documento, FilaTabla, Seccion, Tabla, TipoBloque,
)


FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


def _doc_ejemplo() -> Documento:
    """Documento sintético para pruebas de generadores."""
    sec1 = Seccion(nivel=1, titulo="Informe Técnico 2026", pagina_origen=1)
    sec1.bloques.append(Bloque(
        tipo=TipoBloque.PARRAFO,
        contenido="El proyecto reporta un avance del 78% con un presupuesto ejecutado.",
        posicion=0,
    ))
    sec2 = Seccion(nivel=2, titulo="1. Indicadores Clave", pagina_origen=1)
    sec2.bloques.append(Bloque(
        tipo=TipoBloque.LISTA,
        contenido="Avance: 78%\nCosto/m²: S/ 1,752",
        items_lista=["Avance: 78%", "Costo/m²: S/ 1,752"],
        posicion=1,
    ))
    sec2.bloques.append(Bloque(
        tipo=TipoBloque.TABLA,
        tabla=Tabla(
            encabezados=["Indicador", "Meta", "Resultado"],
            filas=[
                FilaTabla(celdas=["Avance físico", "75%", "78%"]),
                FilaTabla(celdas=["Costo por m²", "S/ 1,800", "S/ 1,752"]),
            ],
            confianza=1.0,
        ),
        posicion=2,
    ))
    sec3 = Seccion(nivel=2, titulo="2. Conclusiones", pagina_origen=2)
    sec3.bloques.append(Bloque(
        tipo=TipoBloque.PARRAFO,
        contenido="El proyecto supera las metas establecidas.",
        posicion=3,
    ))
    return Documento(
        titulo="Informe Técnico 2026",
        autor="COSAPI S.A.",
        idioma="es",
        origen=FIXTURES / "informe_obra.md",
        formato_origen="md",
        paginas=2,
        secciones=[sec1, sec2, sec3],
    )


class TestGeneradorDOCX:
    def setup_method(self):
        from txt2media.generadores.generador_docx import GeneradorDOCX
        self.gen = GeneradorDOCX()

    def test_formato_es_docx(self):
        assert self.gen.formato == "docx"

    def test_genera_archivo_docx(self, tmp_path):
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "salida.docx", {})
        assert ruta.exists()
        assert ruta.suffix == ".docx"
        assert ruta.stat().st_size > 0

    def test_docx_contiene_titulo(self, tmp_path):
        from docx import Document as DocxDocument
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.docx", {})
        docx = DocxDocument(str(ruta))
        textos = [p.text for p in docx.paragraphs if p.text.strip()]
        assert any("Informe Técnico 2026" in t for t in textos)

    def test_docx_contiene_tabla(self, tmp_path):
        from docx import Document as DocxDocument
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.docx", {})
        docx = DocxDocument(str(ruta))
        assert len(docx.tables) >= 1

    def test_genera_con_escritura_atomica(self, tmp_path):
        """El archivo destino existe y no hay archivos temporales huérfanos."""
        doc = _doc_ejemplo()
        ruta_dest = tmp_path / "atomico.docx"
        self.gen.generar(doc, ruta_dest, {})
        archivos = list(tmp_path.iterdir())
        assert ruta_dest in archivos
        assert len(archivos) == 1  # Solo el archivo final


class TestGeneradorXLSX:
    def setup_method(self):
        from txt2media.generadores.generador_xlsx import GeneradorXLSX
        self.gen = GeneradorXLSX()

    def test_formato_es_xlsx(self):
        assert self.gen.formato == "xlsx"

    def test_genera_archivo_xlsx(self, tmp_path):
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "salida.xlsx", {})
        assert ruta.exists()
        assert ruta.suffix == ".xlsx"
        assert ruta.stat().st_size > 0

    def test_xlsx_tiene_hoja_por_seccion(self, tmp_path):
        import openpyxl
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.xlsx", {})
        wb = openpyxl.load_workbook(str(ruta))
        assert len(wb.sheetnames) >= 1

    def test_xlsx_contiene_datos_tabla(self, tmp_path):
        import openpyxl
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.xlsx", {})
        wb = openpyxl.load_workbook(str(ruta))
        ws = wb.active
        # Debe tener datos en alguna celda
        datos = [ws.cell(row=r, column=c).value for r in range(1, 10) for c in range(1, 5)]
        assert any(d is not None and str(d).strip() for d in datos)


class TestGeneradorPPTX:
    def setup_method(self):
        from txt2media.generadores.generador_pptx import GeneradorPPTX
        self.gen = GeneradorPPTX()

    def test_formato_es_pptx(self):
        assert self.gen.formato == "pptx"

    def test_genera_archivo_pptx(self, tmp_path):
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "salida.pptx", {})
        assert ruta.exists()
        assert ruta.suffix == ".pptx"
        assert ruta.stat().st_size > 0

    def test_pptx_tiene_diapositivas(self, tmp_path):
        from pptx import Presentation
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.pptx", {})
        prs = Presentation(str(ruta))
        assert len(prs.slides) >= 1

    def test_pptx_primera_diapositiva_tiene_titulo(self, tmp_path):
        from pptx import Presentation
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.pptx", {})
        prs = Presentation(str(ruta))
        slide = prs.slides[0]
        textos = " ".join(
            shape.text_frame.text
            for shape in slide.shapes
            if shape.has_text_frame
        )
        assert "Informe Técnico" in textos

    def test_pptx_diapositiva_16_9(self, tmp_path):
        from pptx import Presentation
        from pptx.util import Inches
        doc = _doc_ejemplo()
        ruta = self.gen.generar(doc, tmp_path / "out.pptx", {})
        prs = Presentation(str(ruta))
        # 16:9 → 10 pulg × 7.5 pulg o 13.33 × 7.5
        ratio = prs.slide_width / prs.slide_height
        assert abs(ratio - 16 / 9) < 0.1
