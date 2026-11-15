"""Tests del sistema de temas."""

from txt2media.core.tema import TEMA


def test_tema_tiene_colores_base() -> None:
    assert TEMA.azul.startswith("#")
    assert TEMA.naranja.startswith("#")
    assert TEMA.verde.startswith("#")


def test_tema_azul_claro_existe() -> None:
    assert hasattr(TEMA, "azul_claro")
    assert TEMA.azul_claro.startswith("#")


def test_tema_fuentes() -> None:
    assert TEMA.fuente_titulo
    assert TEMA.fuente_cuerpo


def test_tema_fondos() -> None:
    assert TEMA.fondo.startswith("#")
    assert TEMA.fondo_oscuro.startswith("#")
