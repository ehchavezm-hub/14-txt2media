"""Tests básicos del orquestador."""

import pytest
from pathlib import Path
from txt2media.core.orquestador import Orquestador
from txt2media.core.modelo import Documento, Seccion, Bloque, TipoBloque


def test_orquestador_instancia() -> None:
    orq = Orquestador()
    assert orq is not None


def test_orquestador_lee_md(tmp_path) -> None:
    md = tmp_path / "test.md"
    md.write_text("# Título\n\nPárrafo de prueba.\n", encoding="utf-8")
    from txt2media.lectores.lector_md import LectorMarkdown
    doc = LectorMarkdown().leer(md)
    assert doc.titulo or doc.secciones
