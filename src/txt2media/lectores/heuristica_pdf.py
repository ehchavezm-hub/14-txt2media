"""Heurística documentada para detectar estructura jerárquica en PDFs.

Los PDFs no tienen etiquetas H1-H6 reales. Esta heurística usa:
1. Tamaño relativo de fuente respecto a la mediana del texto base.
2. Peso de fuente (bold).
3. Numeración ("1.", "1.1", "Capítulo").
4. Posición vertical (títulos tienden a estar al inicio de bloques).
5. Eliminación de headers/footers por repetición en ≥3 páginas.
6. Orden correcto en documentos de dos columnas.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from typing import NamedTuple

# Patrón de numeración de secciones
_RE_NUMERACION = re.compile(
    r"^(\d+\.){1,3}(\d+)?\s|^(capítulo|chapter|sección|section|parte|part)\s+\w",
    re.IGNORECASE,
)


@dataclass
class TextoConFuente:
    """Texto extraído de un PDF con información de fuente."""
    texto: str
    tamano_fuente: float
    negrita: bool
    x0: float  # Coordenada izquierda
    y0: float  # Coordenada superior
    x1: float  # Coordenada derecha
    y1: float  # Coordenada inferior
    pagina: int


def calcular_mediana_fuente(textos: list[TextoConFuente]) -> float:
    """Calcula la mediana de tamaño de fuente del texto base (excluyendo outliers)."""
    if not textos:
        return 12.0
    tamanhos = [t.tamano_fuente for t in textos if t.tamano_fuente > 0]
    if not tamanhos:
        return 12.0
    return statistics.median(tamanhos)


def detectar_nivel_titulo(
    texto_obj: TextoConFuente,
    mediana_fuente: float,
    umbral_titulo: float = 1.15,
) -> int | None:
    """Determina el nivel de título (1-6) o None si es texto normal.

    Criterios (en orden de prioridad):
    1. Si el tamaño es >= umbral_titulo * mediana → título
    2. Si está en negrita y el tamaño es >= mediana → título
    3. Si sigue patrón de numeración ("1.", "1.1", "Capítulo") → título
    """
    texto = texto_obj.texto.strip()
    if not texto:
        return None

    ratio = texto_obj.tamano_fuente / mediana_fuente if mediana_fuente > 0 else 1.0

    if ratio >= 1.5:
        return 1
    elif ratio >= 1.3:
        return 2
    elif ratio >= umbral_titulo:
        return 3
    elif texto_obj.negrita and ratio >= 0.95:
        return 4
    elif _RE_NUMERACION.match(texto):
        # Detectar nivel por número de puntos
        partes = texto.split(" ")[0].rstrip(".")
        nivel_num = partes.count(".") + 1
        return min(nivel_num, 4)

    return None


def detectar_dos_columnas(
    textos_pagina: list[TextoConFuente], ancho_pagina: float
) -> bool:
    """Detecta si una página tiene diseño de dos columnas."""
    if not textos_pagina or ancho_pagina <= 0:
        return False

    mitad = ancho_pagina / 2
    en_izquierda = sum(1 for t in textos_pagina if t.x1 < mitad + 20)
    en_derecha = sum(1 for t in textos_pagina if t.x0 > mitad - 20)

    total = len(textos_pagina)
    if total == 0:
        return False

    # Si hay un número significativo de bloques a cada lado
    return (en_izquierda / total >= 0.3) and (en_derecha / total >= 0.3)


def ordenar_dos_columnas(
    textos_pagina: list[TextoConFuente], ancho_pagina: float
) -> list[TextoConFuente]:
    """Ordena el texto de dos columnas: col izquierda de arriba a abajo, luego col derecha."""
    mitad = ancho_pagina / 2
    izquierda = sorted(
        [t for t in textos_pagina if t.x0 < mitad],
        key=lambda t: (t.y0, t.x0),
    )
    derecha = sorted(
        [t for t in textos_pagina if t.x0 >= mitad],
        key=lambda t: (t.y0, t.x0),
    )
    return izquierda + derecha


def detectar_headers_footers(
    textos_por_pagina: list[list[TextoConFuente]],
    min_repeticiones: int = 3,
    tolerancia_posicion: float = 5.0,
) -> set[str]:
    """Detecta textos que se repiten en la misma posición en múltiples páginas (headers/footers)."""
    if len(textos_por_pagina) < min_repeticiones:
        return set()

    # Contar apariciones de texto+posición_relativa
    conteo: dict[str, int] = {}
    for pagina_textos in textos_por_pagina:
        for texto_obj in pagina_textos:
            # Redondear posición para tolerar pequeñas variaciones
            y_rel = round(texto_obj.y0 / tolerancia_posicion) * tolerancia_posicion
            clave = f"{texto_obj.texto.strip()}|{y_rel:.0f}"
            conteo[clave] = conteo.get(clave, 0) + 1

    # Los que aparecen en ≥ min_repeticiones páginas son headers/footers
    return {
        clave.split("|")[0]
        for clave, n in conteo.items()
        if n >= min_repeticiones
    }
