"""Tests para generadores DOCX, XLSX y PPTX."""

import pytest
from pathlib import Path

from txt2media.core.modelo import (
    Bloque, Documento, FilaTabla, Seccion, Tabla, TipoBloque,
)


def _doc_ejemplo() -> Documento:
    sec1 = Seccion(nivel=1, titulo="Informe Técnico 2026")
    sec1.bloques.append(Bloque(
        tipo=TipoBloque.PARRAFO,
        contenido="El proyecto reporta un avance del 78% con un presupuesto ejecutado.",
    ))
    sec1.bloques.append(Bloque(
        tipo=TipoBloque.PARRAFO,
        contenido="Texto en negrita importante.",
        negrita=True,
    ))
    sec2 = Seccion(nivel=2, titulo="1. Indicadores Clave")
    sec2.bloques.append(Bloque(
        tipo=TipoBloque.LISTA,
        items_lista=["Avance: 78%", "Costo/m²: S/ 1,752"],
    ))
    sec2.bloques.append(Bloque(
        tipo=TipoBloque.TABLA,
        tabla=Tabla(
            encabezados=["Indicador", "Meta", "Resultado"],
            filas=[
                FilaTabla(celdas=["Avance físico", "75%", "78%"]),
                FilaTabla(celdas=["Costo por m²", "S/ 1,800", "S/ 1,752"]),
            ],
        ),
    ))
    sec2.bloques.append(Bloque(
        tipo=TipoBloque.CAPTION,
        contenido="Tabla 1: Indicadores de desempeño.",
    ))
    sec3 = Seccion(nivel=2, titulo="2. Conclusiones")
    sec3.bloques.append(Bloque(
        tipo=TipoBloque.PARRAFO,
        contenido="El proyecto supera las metas establecidas.",
    ))
    sec3.bloques.append(Bloque(
        tipo=TipoBloque.NOTA_PIE,
        contenido="1. Fuente: Informe de avance semanal.",
    ))
    return Documento(
        titulo="Informe Técnico 2026",
        autor="COSAPI S.A.",
        idioma="es",
        secciones=[sec1, sec2, sec3],
    )


class TestGeneradorDOCX:
    def setup_method(self):
        from txt2media.generadores.generador_docx import GeneradorDOCX
        self.gen = GeneradorDOCX()

    def test_genera_archivo_docx(self, tmp_path):
        doc = _doc_ejemplo()
        ruta = tmp_path / "salida.docx"
        self.gen.generar(doc, ruta, {})
        assert ruta.exists()
        assert ruta.suffix == ".docx"
        assert ruta.stat().st_size > 0

    def test_docx_contiene_titulo(self, tmp_path):
        from docx import Document as DocxDocument
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.docx"
        self.gen.generar(doc, ruta, {})
        docx = DocxDocument(str(ruta))
        textos = [p.text for p in docx.paragraphs if p.text.strip()]
        assert any("Informe Técnico 2026" in t for t in textos)

    def test_docx_contiene_tabla(self, tmp_path):
        from docx import Document as DocxDocument
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.docx"
        self.gen.generar(doc, ruta, {})
        docx = DocxDocument(str(ruta))
        assert len(docx.tables) >= 1

    def test_docx_negrita_cursiva(self, tmp_path):
        from docx import Document as DocxDocument
        doc = Documento(
            titulo="Test",
            secciones=[Seccion(nivel=1, titulo="S", bloques=[
                Bloque(tipo=TipoBloque.PARRAFO, contenido="bold text", negrita=True),
                Bloque(tipo=TipoBloque.PARRAFO, contenido="italic text", cursiva=True),
            ])]
        )
        ruta = tmp_path / "bold.docx"
        self.gen.generar(doc, ruta, {})
        docx = DocxDocument(str(ruta))
        runs = [r for p in docx.paragraphs for r in p.runs if r.text]
        assert any(r.bold for r in runs)
        assert any(r.italic for r in runs)

    def test_docx_caption_nota_pie(self, tmp_path):
        from docx import Document as DocxDocument
        doc = Documento(
            titulo="Test",
            secciones=[Seccion(nivel=1, titulo="S", bloques=[
                Bloque(tipo=TipoBloque.CAPTION, contenido="Figura 1."),
                Bloque(tipo=TipoBloque.NOTA_PIE, contenido="1. Fuente: Reporte."),
            ])]
        )
        ruta = tmp_path / "cap.docx"
        self.gen.generar(doc, ruta, {})
        docx = DocxDocument(str(ruta))
        textos = [p.text for p in docx.paragraphs if p.text.strip()]
        assert any("Figura 1." in t for t in textos)
        assert any("Fuente: Reporte" in t for t in textos)


class TestGeneradorXLSX:
    def setup_method(self):
        from txt2media.generadores.generador_xlsx import GeneradorXLSX
        self.gen = GeneradorXLSX()

    def test_genera_archivo_xlsx(self, tmp_path):
        doc = _doc_ejemplo()
        ruta = tmp_path / "salida.xlsx"
        self.gen.generar(doc, ruta, {})
        assert ruta.exists()
        assert ruta.suffix == ".xlsx"
        assert ruta.stat().st_size > 0

    def test_xlsx_tiene_hoja_por_seccion(self, tmp_path):
        import openpyxl
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.xlsx"
        self.gen.generar(doc, ruta, {})
        wb = openpyxl.load_workbook(str(ruta))
        assert len(wb.sheetnames) >= 1

    def test_xlsx_contiene_datos_tabla(self, tmp_path):
        import openpyxl
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.xlsx"
        self.gen.generar(doc, ruta, {})
        wb = openpyxl.load_workbook(str(ruta))
        ws = wb.active
        datos = [ws.cell(row=r, column=c).value for r in range(1, 10) for c in range(1, 5)]
        assert any(d is not None and str(d).strip() for d in datos)

    def test_xlsx_caption_nota_pie(self, tmp_path):
        import openpyxl
        doc = Documento(
            titulo="Test",
            secciones=[Seccion(nivel=1, titulo="S", bloques=[
                Bloque(tipo=TipoBloque.CAPTION, contenido="Pie de figura."),
                Bloque(tipo=TipoBloque.NOTA_PIE, contenido="Nota al pie."),
            ])]
        )
        ruta = tmp_path / "cap.xlsx"
        self.gen.generar(doc, ruta, {})
        wb = openpyxl.load_workbook(str(ruta))
        all_values = []
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value:
                        all_values.append(str(cell.value))
        assert any("Pie de figura" in v for v in all_values)
        assert any("Nota al pie" in v for v in all_values)


class TestGeneradorPPTX:
    def setup_method(self):
        from txt2media.generadores.generador_pptx import GeneradorPPTX
        self.gen = GeneradorPPTX()

    def test_genera_archivo_pptx(self, tmp_path):
        doc = _doc_ejemplo()
        ruta = tmp_path / "salida.pptx"
        self.gen.generar(doc, ruta, {})
        assert ruta.exists()
        assert ruta.suffix == ".pptx"
        assert ruta.stat().st_size > 0

    def test_pptx_tiene_diapositivas(self, tmp_path):
        from pptx import Presentation
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.pptx"
        self.gen.generar(doc, ruta, {})
        prs = Presentation(str(ruta))
        assert len(prs.slides) >= 1

    def test_pptx_primera_diapositiva_tiene_titulo(self, tmp_path):
        from pptx import Presentation
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.pptx"
        self.gen.generar(doc, ruta, {})
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
        doc = _doc_ejemplo()
        ruta = tmp_path / "out.pptx"
        self.gen.generar(doc, ruta, {})
        prs = Presentation(str(ruta))
        ratio = prs.slide_width / prs.slide_height
        assert abs(ratio - 16 / 9) < 0.1
