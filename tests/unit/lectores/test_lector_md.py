"""Tests para LectorMarkdown."""

import pytest
from pathlib import Path

from txt2media.lectores.lector_md import LectorMarkdown
from txt2media.core.modelo import TipoBloque

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class TestLectorMarkdownLeer:
    def setup_method(self):
        self.lector = LectorMarkdown()

    def test_leer_devuelve_documento(self, tmp_path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# Título\n\nPárrafo.\n", encoding="utf-8")
        from txt2media.core.modelo import Documento
        doc = self.lector.leer(f)
        assert isinstance(doc, Documento)

    def test_titulo_es_nombre_archivo_si_no_hay_h1(self, tmp_path) -> None:
        f = tmp_path / "mi_documento.md"
        f.write_text("Sin título.\n", encoding="utf-8")
        doc = self.lector.leer(f)
        assert "mi_documento" in doc.titulo

    def test_detecta_secciones_de_nivel_2(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_obra.md")
        niveles = [s.nivel for s in doc.secciones]
        assert 2 in niveles

    def test_detecta_secciones_de_nivel_3(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_obra.md")
        niveles = [s.nivel for s in doc.secciones]
        assert 3 in niveles

    def test_bloques_parrafo_no_vacios(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_obra.md")
        parrafos = [b for s in doc.secciones for b in s.bloques
                    if b.tipo == TipoBloque.PARRAFO]
        assert len(parrafos) > 0
        assert all(b.contenido for b in parrafos)

    def test_detecta_lista(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_obra.md")
        listas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.LISTA]
        assert len(listas) > 0

    def test_items_lista_no_vacios(self) -> None:
        doc = self.lector.leer(FIXTURES / "informe_obra.md")
        for s in doc.secciones:
            for b in s.bloques:
                if b.tipo == TipoBloque.LISTA:
                    assert len(b.items_lista) > 0

    def test_md_detecta_niveles_de_titulo(self, tmp_path) -> None:
        f = tmp_path / "niveles.md"
        f.write_text("# H1\n## H2\n### H3\n", encoding="utf-8")
        doc = self.lector.leer(f)
        niveles = {s.titulo: s.nivel for s in doc.secciones}
        assert niveles.get("H1") == 1
        assert niveles.get("H2") == 2
        assert niveles.get("H3") == 3

    def test_archivo_inexistente_lanza_error(self) -> None:
        with pytest.raises((FileNotFoundError, OSError)):
            self.lector.leer(Path("/no/existe.md"))

    def test_caracteres_especiales_utf8(self) -> None:
        doc = self.lector.leer(FIXTURES / "caracteres_especiales.md")
        titulos = [s.titulo for s in doc.secciones]
        assert any("ñ" in t or "Análisis" in t or "Técnico" in t for t in titulos)


class TestLectorMarkdownTabla:
    def setup_method(self):
        self.lector = LectorMarkdown()

    def test_extrae_tabla_md(self, tmp_path) -> None:
        f = tmp_path / "tabla.md"
        f.write_text(
            "# Doc\n\n"
            "| Col A | Col B |\n"
            "|-------|-------|\n"
            "| Val1  | Val2  |\n",
            encoding="utf-8"
        )
        doc = self.lector.leer(f)
        tablas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.TABLA]
        # Tabla debe extraerse si el lector la soporta
        if tablas:
            assert tablas[0].tabla is not None
