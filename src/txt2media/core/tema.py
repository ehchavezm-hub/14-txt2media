"""Tema visual Tableau 10 + Figtree para txt2media."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemaTableau:
    # Paleta Tableau 10
    azul:     str = "#4E79A7"
    naranja:  str = "#F28E2B"
    rojo:     str = "#E15759"
    cian:     str = "#76B7B2"
    verde:    str = "#59A14F"
    amarillo: str = "#EDC948"
    violeta:  str = "#B07AA1"
    rosa:     str = "#FF9DA7"
    marron:   str = "#9C755F"
    gris:     str = "#BAB0AC"

    # Tipografía
    fuente_titulo: str = "Figtree"
    fuente_cuerpo: str = "Figtree"
    tam_titulo: int = 40
    tam_subtitulo: int = 28
    tam_cuerpo: int = 18

    # Colores UI
    fondo: str = "#FFFFFF"
    fondo_oscuro: str = "#1E1E1E"
    texto: str = "#1A1A1A"
    texto_claro: str = "#F5F5F5"
    azul_claro: str = "#6B9DC4"


TEMA = TemaTableau()

COLORES_SERIES = [
    TEMA.azul, TEMA.naranja, TEMA.rojo, TEMA.cian,
    TEMA.verde, TEMA.amarillo, TEMA.violeta, TEMA.rosa,
    TEMA.marron, TEMA.gris,
]
