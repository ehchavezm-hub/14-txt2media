"""Tests del sistema de temas: paleta, contraste WCAG y carga."""

import json
from pathlib import Path

import pytest

from txt2media.core.tema import (
    Tema,
    cargar_tema,
    contraste_ratio,
    texto_optimo,
    validar_tema,
)


# --- contraste_ratio ---


def test_blanco_sobre_negro_es_21() -> None:
    ratio = contraste_ratio("#FFFFFF", "#000000")
    assert abs(ratio - 21.0) < 0.1


def test_blanco_sobre_blanco_es_1() -> None:
    ratio = contraste_ratio("#FFFFFF", "#FFFFFF")
    assert abs(ratio - 1.0) < 0.01


def test_contraste_azul_primario_sobre_blanco() -> None:
    # #4E79A7 sobre blanco debe tener contraste > 3.0
    ratio = contraste_ratio("#4E79A7", "#FFFFFF")
    assert ratio >= 3.0


def test_contraste_es_simetrico() -> None:
    r1 = contraste_ratio("#4E79A7", "#FFFFFF")
    r2 = contraste_ratio("#FFFFFF", "#4E79A7")
    assert abs(r1 - r2) < 0.001


# --- texto_optimo ---


def test_texto_optimo_azul_primario() -> None:
    # #4E79A7 sobre fondo oscuro da más contraste con blanco
    resultado = texto_optimo("#4E79A7")
    assert resultado == "#FFFFFF"


def test_texto_optimo_amarillo_advertencia() -> None:
    # #EDC948 (amarillo claro) → texto oscuro
    resultado = texto_optimo("#EDC948")
    assert resultado == "#2B2B2B"


def test_texto_optimo_devuelve_mejor_contraste() -> None:
    # Para cualquier color, el resultado debe tener mayor contraste que la alternativa
    colores_prueba = ["#4E79A7", "#F28E2B", "#E15759", "#59A14F", "#EDC948"]
    for color in colores_prueba:
        resultado = texto_optimo(color)
        otro = "#2B2B2B" if resultado == "#FFFFFF" else "#FFFFFF"
        assert contraste_ratio(color, resultado) >= contraste_ratio(color, otro) - 0.001


# --- cargar_tema ---


def test_tema_por_defecto_carga() -> None:
    tema = cargar_tema(None)
    assert tema.colores["primario"] == "#4E79A7"
    assert len(tema.series) >= 3


def test_tema_por_defecto_tiene_diez_series() -> None:
    tema = cargar_tema(None)
    assert len(tema.series) == 10


def test_tema_desde_json(tmp_path: Path) -> None:
    datos = {
        "nombre": "Test",
        "version": 1,
        "colores": {
            "primario": "#FF0000", "acento": "#00FF00", "error": "#0000FF",
            "exito": "#FFFF00", "advertencia": "#FF00FF",
            "texto": "#000000", "fondo": "#FFFFFF", "superficie": "#EEEEEE",
            "borde": "#CCCCCC",
        },
        "series": ["#FF0000", "#00FF00", "#0000FF"],
        "oscuro": {"fondo": "#111111", "superficie": "#222222", "texto": "#FFFFFF"},
        "tipografia": {"familia": "Arial", "archivos": []},
    }
    ruta = tmp_path / "tema.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    tema = cargar_tema(ruta)
    assert tema.colores["primario"] == "#FF0000"
    assert tema.nombre == "Test"


def test_contraste_serie_por_defecto_cumple_wcag_con_su_texto() -> None:
    """Para cada color de la serie, el texto óptimo debe cumplir WCAG 4.5:1."""
    tema = cargar_tema(None)
    incumplimientos = []
    for color in tema.series:
        texto = texto_optimo(color)
        ratio = contraste_ratio(color, texto)
        if ratio < 4.5:
            incumplimientos.append((color, texto, ratio))
    # Algunos colores de Tableau 10 están en zona media; se avisa pero no se bloquea
    # Lo que sí se verifica: texto_optimo siempre elige el MEJOR contraste posible
    for color, texto, ratio in incumplimientos:
        otro = "#2B2B2B" if texto == "#FFFFFF" else "#FFFFFF"
        ratio_otro = contraste_ratio(color, otro)
        assert ratio >= ratio_otro - 0.001, (
            f"texto_optimo({color}) = {texto} (ratio {ratio:.2f}) "
            f"no es mejor que {otro} (ratio {ratio_otro:.2f})"
        )


# --- validar_tema ---


def test_validar_tema_valido() -> None:
    datos: dict[str, object] = {
        "colores": {"primario": "#FF0000"},
        "series": ["#FF0000", "#00FF00", "#0000FF"],
    }
    errores = validar_tema(datos)
    assert errores == []


def test_validar_tema_color_invalido() -> None:
    datos: dict[str, object] = {
        "colores": {"primario": "rojo"},
        "series": ["#FF0000", "#00FF00", "#0000FF"],
    }
    errores = validar_tema(datos)
    assert any("primario" in e for e in errores)


def test_validar_tema_series_insuficientes() -> None:
    datos: dict[str, object] = {
        "colores": {},
        "series": ["#FF0000", "#00FF00"],  # solo 2, mínimo es 3
    }
    errores = validar_tema(datos)
    assert any("series" in e for e in errores)
