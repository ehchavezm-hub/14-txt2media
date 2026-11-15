"""Tests para LectorEPUB."""

import pytest
import zipfile
from pathlib import Path

from txt2media.lectores.lector_epub import LectorEPUB
from txt2media.core.modelo import TipoBloque

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class TestLectorEPUBFormatos:
    def setup_method(self):
        self.lector = LectorEPUB()

    def test_formatos_soportados_incluye_epub(self):
        assert ".epub" in self.lector.formatos_soportados

    def test_puede_leer_epub(self):
        assert self.lector.puede_leer(FIXTURES / "libro_tecnico.epub") is True


class TestLectorEPUBLeerFixture:
    def setup_method(self):
        self.lector = LectorEPUB()
        self.doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")

    def test_titulo_del_opf(self):
        assert "Manual Técnico" in self.doc.titulo or "Construcción" in self.doc.titulo

    def test_autor_del_opf(self):
        assert "COSAPI" in (self.doc.autor or "")

    def test_idioma_detectado(self):
        assert self.doc.idioma in ("es", "ca", "pt", "gl")

    def test_secciones_detectadas(self):
        assert len(self.doc.secciones) > 0

    def test_formato_origen_es_epub(self):
        assert self.doc.formato_origen == "epub"


class TestLectorEPUBOrdenSpine:
    def setup_method(self):
        self.lector = LectorEPUB()

    def test_epub_respeta_orden_spine(self):
        """El capítulo 1 debe aparecer antes del capítulo 2 en el orden de secciones."""
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        titulos = [s.titulo for s in doc.secciones]
        idx_cap1 = next((i for i, t in enumerate(titulos) if "1" in t and "Cap" in t), None)
        idx_cap2 = next((i for i, t in enumerate(titulos) if "2" in t and "Cap" in t), None)
        assert idx_cap1 is not None
        assert idx_cap2 is not None
        assert idx_cap1 < idx_cap2

    def test_secciones_h1_son_nivel_1(self):
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        h1s = [s for s in doc.secciones if s.nivel == 1]
        assert len(h1s) >= 2  # Hay 2 capítulos

    def test_secciones_h2_son_nivel_2(self):
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        h2s = [s for s in doc.secciones if s.nivel == 2]
        assert len(h2s) >= 2  # 1.1 Materiales y 2.1 Etapas

    def test_bloques_parrafo_no_vacios(self):
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        parrafos = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.PARRAFO
        ]
        assert len(parrafos) > 0

    def test_lista_extraida(self):
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        listas = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.LISTA
        ]
        assert len(listas) > 0

    def test_tabla_extraida(self):
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        tablas = [
            b for s in doc.secciones
            for b in s.bloques
            if b.tipo == TipoBloque.TABLA
        ]
        assert len(tablas) >= 1


class TestLectorEPUBSeguridad:
    def setup_method(self):
        self.lector = LectorEPUB()

    def test_epub_zip_malicioso_rechazado(self):
        """Un EPUB con rutas '../' debe ser rechazado por validar_zip."""
        with pytest.raises(ValueError, match="no seguro|maliciosa|malicious|RutaMaliciosa"):
            self.lector.leer(FIXTURES / "zip_malicioso.zip")

    def test_archivo_inexistente_lanza_error(self):
        with pytest.raises(FileNotFoundError):
            self.lector.leer(Path("/no/existe.epub"))

    def test_epub_corrupto_lanza_valor_error(self, tmp_path):
        f = tmp_path / "corrupto.epub"
        f.write_bytes(b"esto no es un zip")
        with pytest.raises(ValueError):
            self.lector.leer(f)

    def test_epub_sin_container_xml_lanza_error(self, tmp_path):
        """EPUB sin META-INF/container.xml es inválido."""
        f = tmp_path / "sin_container.epub"
        with zipfile.ZipFile(f, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            zf.writestr("content.opf", "<package/>")
        with pytest.raises(ValueError, match="container"):
            self.lector.leer(f)
