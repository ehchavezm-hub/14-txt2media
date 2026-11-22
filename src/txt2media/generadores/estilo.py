"""Identidad visual común de los entregables (HTML, Markdown, Word).

Misma línea que la ventana de la app: azul de señal, Figtree para títulos y
una serifa de lectura para el cuerpo. Los colores de capítulo rotan por una
paleta sobria para que cada sección se reconozca en el índice.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from txt2media.core.modelo import Documento, Seccion, TipoBloque


@dataclass(frozen=True)
class Paleta:
    tinta: str = "#12171D"
    tinta_2: str = "#4E5865"
    tinta_3: str = "#8A939E"
    fondo: str = "#FFFFFF"
    papel: str = "#F6F8FB"
    linea: str = "#E3E7EE"
    acento: str = "#1F64D6"
    acento_2: str = "#4F46E5"
    acento_suave: str = "#EAF1FD"


PALETA = Paleta()

# Colores de capítulo: rotan por sección (marcadores del índice, números, filetes).
COLORES_CAPITULO = [
    "#1F64D6",  # azul
    "#0E7C72",  # verde azulado
    "#4F46E5",  # índigo
    "#C2410C",  # terracota
    "#7C3AED",  # violeta
    "#0369A1",  # azul petróleo
    "#B45309",  # ámbar
    "#BE185D",  # frambuesa
]


def color_capitulo(indice: int) -> str:
    return COLORES_CAPITULO[indice % len(COLORES_CAPITULO)]


def numeracion(secciones: list[Seccion]) -> list[str]:
    """Numeración jerárquica 1, 1.1, 1.2, 2… según el nivel de cada sección."""
    if not secciones:
        return []
    base = min(s.nivel or 1 for s in secciones)
    contadores = [0] * 7
    salida = []
    for s in secciones:
        nivel = max(1, min(6, (s.nivel or 1) - base + 1))
        contadores[nivel] += 1
        for k in range(nivel + 1, 7):
            contadores[k] = 0
        for k in range(1, nivel):
            if contadores[k] == 0:
                contadores[k] = 1
        salida.append(".".join(str(contadores[k]) for k in range(1, nivel + 1)))
    return salida


def nivel_relativo(secciones: list[Seccion], s: Seccion) -> int:
    base = min((x.nivel or 1) for x in secciones) if secciones else 1
    return max(1, min(6, (s.nivel or 1) - base + 1))


def palabras_de(doc: Documento) -> int:
    total = 0
    for s in doc.secciones:
        total += len(s.titulo.split())
        for b in s.bloques:
            if b.tipo in (TipoBloque.PARRAFO, TipoBloque.CITA, TipoBloque.CAPTION, TipoBloque.NOTA_PIE):
                total += len(b.contenido.split())
            elif b.tipo == TipoBloque.LISTA:
                total += sum(len(i.split()) for i in b.items_lista)
            elif b.tipo == TipoBloque.TABLA and b.tabla:
                total += sum(len(c.split()) for f in b.tabla.filas for c in f.celdas)
    return total


def minutos_lectura(palabras: int) -> int:
    return max(1, round(palabras / 220))


def formato_miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def slug_github(texto: str, usados: dict[str, int] | None = None) -> str:
    """Ancla compatible con GitHub/MarkText: minúsculas, sin puntuación, espacios a guiones."""
    t = texto.strip().lower()
    t = "".join(c for c in t if c.isalnum() or c in " -_" or unicodedata.category(c).startswith("M"))
    t = t.replace(" ", "-")
    if usados is not None:
        n = usados.get(t, 0)
        usados[t] = n + 1
        if n:
            t = f"{t}-{n}"
    return t


_RE_PORCENTAJE = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?\s?%)")
_RE_SIGLA = re.compile(r"(?<![\w&;#])([A-ZÁÉÍÓÚÑ]{2,6})(?![\w])")
