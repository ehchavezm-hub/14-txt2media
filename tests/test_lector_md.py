"""Tests del lector Markdown."""
import tempfile
from pathlib import Path

import pytest

from txt2media.lectores.lector_md import LectorMarkdown
from txt2media.core.modelo import TipoBloque


MARKDOWN_BASICO = """\
# Título principal

Párrafo de introducción.

## Sección uno

Texto de la sección uno.

- Item A
- Item B
- Item C

## Sección dos

> Una cita importante

```python
print("hola")
```
"""


@pytest.fixture
def archivo_md(tmp_path):
    ruta = tmp_path / "test.md"
    ruta.write_text(MARKDOWN_BASICO, encoding="utf-8")
    return ruta


def test_leer_titulo(archivo_md):
    doc = LectorMarkdown().leer(archivo_md)
    assert doc.titulo == "test"


def test_leer_secciones(archivo_md):
    doc = LectorMarkdown().leer(archivo_md)
    titulos = [s.titulo for s in doc.secciones]
    assert "Título principal" in titulos


def test_detecta_lista(archivo_md):
    doc = LectorMarkdown().leer(archivo_md)
    todos_bloques = [b for s in doc.secciones for b in s.bloques]
    tipos = [b.tipo for b in todos_bloques]
    assert TipoBloque.LISTA in tipos


def test_detecta_parrafo(archivo_md):
    doc = LectorMarkdown().leer(archivo_md)
    todos_bloques = [b for s in doc.secciones for b in s.bloques]
    parrafos = [b for b in todos_bloques if b.tipo == TipoBloque.PARRAFO]
    assert len(parrafos) >= 1
