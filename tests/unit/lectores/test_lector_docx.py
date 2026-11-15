"""Tests para LectorDOCX."""

import pytest
from pathlib import Path

from txt2media.lectores.lector_docx import LectorDOCX
from txt2media.core.modelo import TipoBloque

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class TestLectorDOCXLeer:
    def setup_method(self):
        self.lector = LectorDOCX()

    def test_leer_devuelve_documento(self) -> None:
        from txt2media.core.modelo import Documento
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        assert isinstance(doc, Documento)

    def test_titulo_detectado(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        assert len(doc.titulo) > 0

    def test_secciones_detectadas(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        assert len(doc.secciones) > 0

    def test_detecta_heading_nivel(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        niveles = [s.nivel for s in doc.secciones]
        assert 1 in niveles or 2 in niveles

    def test_parrafos_no_vacios(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        parrafos = [b for s in doc.secciones for b in s.bloques
                    if b.tipo == TipoBloque.PARRAFO]
        assert len(parrafos) > 0
        assert all(b.contenido for b in parrafos)

    def test_negrita_cursiva_detectadas(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        # Solo verifica que los atributos existen; algunos párrafos pueden ser bold
        parrafos = [b for s in doc.secciones for b in s.bloques
                    if b.tipo == TipoBloque.PARRAFO]
        assert all(isinstance(b.negrita, bool) for b in parrafos)
        assert all(isinstance(b.cursiva, bool) for b in parrafos)


class TestLectorDOCXTabla:
    def setup_method(self):
        self.lector = LectorDOCX()

    def test_docx_extrae_tabla(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.TABLA]
        assert len(tablas) >= 1

    def test_tabla_tiene_encabezados(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.TABLA]
        t = tablas[0].tabla
        assert t is not None
        assert len(t.encabezados) >= 1

    def test_tabla_tiene_filas(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_gestion.docx")
        tablas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.TABLA]
        t = tablas[0].tabla
        assert t is not None
        assert len(t.filas) >= 1


class TestLectorDOCXErrores:
    def setup_method(self):
        self.lector = LectorDOCX()

    def test_archivo_inexistente_lanza_error(self) -> None:
        with pytest.raises((FileNotFoundError, OSError, Exception)):
            self.lector.leer(Path("/no/existe.docx"))

    def test_archivo_no_docx_lanza_error(self, tmp_path) -> None:
        f = tmp_path / "falso.docx"
        f.write_bytes(b"esto no es un docx")
        with pytest.raises(Exception):
            self.lector.leer(f)
