"""Tests para LectorMarkdown."""

import pytest
from pathlib import Path

from txt2media.lectores.lector_md import LectorMarkdown
from txt2media.core.modelo import TipoBloque

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class TestLectorMarkdownFormatos:
    def setup_method(self):
        self.lector = LectorMarkdown()

    def test_formatos_soportados_incluye_md(self):
        assert ".md" in self.lector.formatos_soportados

    def test_formatos_soportados_incluye_markdown(self):
        assert ".markdown" in self.lector.formatos_soportados

    def test_puede_leer_md(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Hola\n")
        assert self.lector.puede_leer(f) is True

    def test_no_puede_leer_pdf(self, tmp_path):
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"%PDF")
        assert self.lector.puede_leer(f) is False


class TestLectorMarkdownLeerFixture:
    def setup_method(self):
        self.lector = LectorMarkdown()
        self.doc = self.lector.leer(FIXTURES / "informe_obra.md")

    def test_detecta_titulo_h1(self):
        assert "Informe Técnico" in self.doc.titulo

    def test_detecta_secciones_de_nivel_2(self):
        niveles = [s.nivel for s in self.doc.secciones]
        assert 2 in niveles

    def test_detecta_secciones_de_nivel_3(self):
        niveles = [s.nivel for s in self.doc.secciones]
        assert 3 in niveles

    def test_bloques_parrafo_no_vacios(self):
        parrafos = [
            b for s in self.doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.PARRAFO
        ]
        assert len(parrafos) > 0
        assert all(b.contenido for b in parrafos)

    def test_detecta_lista(self):
        listas = [
            b for s in self.doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.LISTA
        ]
        assert len(listas) > 0

    def test_items_lista_no_vacios(self):
        for s in self.doc.secciones:
            for b in s.bloques:
                if b.tipo == TipoBloque.LISTA:
                    assert len(b.items_lista) > 0

    def test_idioma_detectado(self):
        assert self.doc.idioma in ("es", "ca", "pt")  # Texto en español

    def test_formato_origen_es_md(self):
        assert self.doc.formato_origen == "md"


class TestLectorMarkdownNivelesTitulo:
    def setup_method(self):
        self.lector = LectorMarkdown()

    def test_md_detecta_niveles_de_titulo(self, tmp_path):
        """Los encabezados # a ###### se mapean a niveles 1-6."""
        contenido = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6\n"
        f = tmp_path / "niveles.md"
        f.write_text(contenido)
        doc = self.lector.leer(f)
        niveles = {s.titulo: s.nivel for s in doc.secciones}
        assert niveles.get("H1") == 1
        assert niveles.get("H2") == 2
        assert niveles.get("H3") == 3

    def test_md_sin_titulo_usa_nombre_archivo(self, tmp_path):
        f = tmp_path / "mi_documento.md"
        f.write_text("Párrafo sin título.\n")
        doc = self.lector.leer(f)
        assert "mi_documento" in doc.titulo

    def test_archivo_inexistente_lanza_error(self):
        with pytest.raises(FileNotFoundError):
            self.lector.leer(Path("/no/existe.md"))

    def test_caracteres_especiales_utf8(self):
        doc = self.lector.leer(FIXTURES / "caracteres_especiales.md")
        titulos = [s.titulo for s in doc.secciones]
        assert any("ñ" in t or "Análisis" in t or "Técnico" in t for t in titulos)


class TestLectorMarkdownTabla:
    def setup_method(self):
        self.lector = LectorMarkdown()

    def test_extrae_tabla_md(self, tmp_path):
        contenido = (
            "# Doc\n\n"
            "| Col A | Col B |\n"
            "|-------|-------|\n"
            "| Val1  | Val2  |\n"
        )
        f = tmp_path / "tabla.md"
        f.write_text(contenido)
        doc = self.lector.leer(f)
        tablas = [
            b for s in doc.secciones for b in s.bloques
            if b.tipo == TipoBloque.TABLA
        ]
        assert len(tablas) == 1
        assert tablas[0].tabla is not None
        assert len(tablas[0].tabla.filas) == 1
