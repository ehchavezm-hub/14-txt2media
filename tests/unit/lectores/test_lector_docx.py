"""Tests para LectorDOCX."""

import pytest
from pathlib import Path

from txt2media.lectores.lector_docx import LectorDOCX
from txt2media.core.modelo import TipoBloque

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class TestLectorDOCXFormatos:
    def setup_method(self):
        self.lector = LectorDOCX()

    def test_formatos_soportados_incluye_docx(self):
        assert ".docx" in self.lector.formatos_soportados

    def test_puede_leer_docx(self):
        assert self.lector.puede_leer(FIXTURES / "informe_gestion.docx") is True

    def test_no_puede_leer_pdf(self, tmp_path):
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"%PDF")
        assert self.lector.puede_leer(f) is False


class TestLectorDOCXLeerFixture:
    def setup_method(self):
        self.lector = LectorDOCX()
        self.doc = self.lector.leer(FIXTURES / "informe_gestion.docx")

    def test_titulo_detectado(self):
        assert len(self.doc.titulo) > 0

    def test_secciones_detectadas(self):
        assert len(self.doc.secciones) > 0

    def test_detecta_heading_nivel_1(self):
        niveles = [s.nivel for s in self.doc.secciones]
        assert 1 in niveles or 2 in niveles  # El fixture tiene H1 y H2

    def test_parrafos_no_vacios(self):
        parrafos = [
            b for s in self.doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.PARRAFO
        ]
        assert len(parrafos) > 0
        assert all(b.contenido for b in parrafos)

    def test_formato_origen_es_docx(self):
        assert self.doc.formato_origen == "docx"

    def test_paginas_positivo(self):
        assert self.doc.paginas >= 1


class TestLectorDOCXExtaerTabla:
    def setup_method(self):
        self.lector = LectorDOCX()

    def test_docx_extrae_tabla(self):
        """El fixture informe_gestion.docx tiene una tabla de 4 filas x 3 cols."""
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.TABLA
        ]
        assert len(tablas) >= 1

    def test_tabla_tiene_encabezados(self):
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.TABLA
        ]
        t = tablas[0].tabla
        assert t is not None
        assert len(t.encabezados) >= 1

    def test_tabla_tiene_filas(self):
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.TABLA
        ]
        t = tablas[0].tabla
        assert t is not None
        assert len(t.filas) >= 1

    def test_tabla_confianza_es_alta(self):
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.TABLA
        ]
        assert tablas[0].tabla.confianza == 1.0


class TestLectorDOCXErrores:
    def setup_method(self):
        self.lector = LectorDOCX()

    def test_archivo_inexistente_lanza_error(self):
        with pytest.raises(FileNotFoundError):
            self.lector.leer(Path("/no/existe.docx"))

    def test_archivo_no_docx_lanza_valor_error(self, tmp_path):
        f = tmp_path / "falso.docx"
        f.write_bytes(b"esto no es un docx")
        with pytest.raises(ValueError):
            self.lector.leer(f)
