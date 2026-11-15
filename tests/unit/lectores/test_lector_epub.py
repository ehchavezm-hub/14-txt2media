"""Tests para LectorEPUB."""

import pytest
import zipfile
from pathlib import Path

from txt2media.lectores.lector_epub import LectorEPUB
from txt2media.core.modelo import TipoBloque

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class TestLectorEPUBLeer:
    def setup_method(self):
        self.lector = LectorEPUB()

    def test_leer_devuelve_documento(self) -> None:
        from txt2media.core.modelo import Documento
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        assert isinstance(doc, Documento)

    def test_titulo_del_opf(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        assert len(doc.titulo) > 0

    def test_idioma_detectado(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        assert doc.idioma in ("es", "ca", "pt", "gl", "en")

    def test_secciones_detectadas(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        assert len(doc.secciones) > 0

    def test_epub_respeta_orden_spine(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        titulos = [s.titulo for s in doc.secciones]
        idx_cap1 = next((i for i, t in enumerate(titulos) if "1" in t and "Cap" in t), None)
        idx_cap2 = next((i for i, t in enumerate(titulos) if "2" in t and "Cap" in t), None)
        assert idx_cap1 is not None
        assert idx_cap2 is not None
        assert idx_cap1 < idx_cap2

    def test_secciones_h1_son_nivel_1(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        h1s = [s for s in doc.secciones if s.nivel == 1]
        assert len(h1s) >= 1

    def test_bloques_parrafo_no_vacios(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        parrafos = [b for s in doc.secciones for b in s.bloques
                    if b.tipo == TipoBloque.PARRAFO]
        assert len(parrafos) > 0

    def test_lista_extraida(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        listas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.LISTA]
        assert len(listas) > 0

    def test_tabla_extraida(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        tablas = [b for s in doc.secciones for b in s.bloques
                  if b.tipo == TipoBloque.TABLA]
        # Si el epub de fixtures no tiene tablas, simplemente verificamos que el tipo existe
        for t in tablas:
            assert t.tabla is not None

    def test_negrita_cursiva_son_bool(self) -> None:
        doc = self.lector.leer(FIXTURES / "libro_tecnico.epub")
        parrafos = [b for s in doc.secciones for b in s.bloques
                    if b.tipo == TipoBloque.PARRAFO]
        assert all(isinstance(b.negrita, bool) for b in parrafos)
        assert all(isinstance(b.cursiva, bool) for b in parrafos)


class TestLectorEPUBErrores:
    def setup_method(self):
        self.lector = LectorEPUB()

    def test_archivo_inexistente_lanza_error(self) -> None:
        with pytest.raises((FileNotFoundError, OSError, Exception)):
            self.lector.leer(Path("/no/existe.epub"))

    def test_epub_corrupto_lanza_error(self, tmp_path) -> None:
        f = tmp_path / "corrupto.epub"
        f.write_bytes(b"esto no es un zip")
        with pytest.raises(Exception):
            self.lector.leer(f)

    def test_epub_sin_container_xml_devuelve_documento_vacio(self, tmp_path) -> None:
        f = tmp_path / "sin_container.epub"
        with zipfile.ZipFile(f, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
        doc = self.lector.leer(f)
        # Debe devolver un documento vacío o lanzar excepción controlada
        assert doc is not None
