"""Lector PDF con detección inteligente de estructura, párrafos y limpieza."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque

# ── Umbrales ────────────────────────────────────────────────────────────────
_UMBRAL_TITULO_PT = 14.0
_MIN_REPETICIONES_HEADER = 3   # veces que debe repetirse en páginas distintas
_ZONA_HEADER = 0.10            # top 10 % de la página
_ZONA_FOOTER = 0.90            # bottom 10 % de la página

# ── Patrones de texto a descartar ───────────────────────────────────────────
_RE_SOLO_NUMERO = re.compile(r"^\s*[\-–—·•]?\s*\d+\s*[\-–—·•]?\s*$")
_RE_PAGINA = re.compile(
    r"^\s*(?:página|page|pág\.?|p\.?)?\s*\d+\s*(?:de|of|/\s*\d+)?\s*$",
    re.IGNORECASE,
)
_RE_SOLO_DECORATIVO = re.compile(r"^[\-–—_=\*\.·•\s]{3,}$")
_RE_TOC_LINEA = re.compile(r"^.{2,}[\.\s]{4,}\d{1,4}\s*$")  # "Título ........ 12"

# ── Marcadores de lista ──────────────────────────────────────────────────────
_RE_LISTA = re.compile(r"^[•○▪▸→►◆\-\*]\s+(.+)$")
_RE_LISTA_NUM = re.compile(r"^\d{1,2}[.)]\s+(.+)$")

# ── Fin de párrafo (puntuación terminal) ────────────────────────────────────
_RE_FIN_PARRAFO = re.compile(r"[.!?]\s*$")
_RE_GUION_FINAL = re.compile(r"-$")

# ── Ligaduras tipográficas ───────────────────────────────────────────────────
_LIGATURES = str.maketrans({
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
    "ﬁ": "fi", "ﬂ": "fl", "­": "",
})


class LectorPDF:
    def leer(self, ruta: Path) -> Documento:
        import pdfplumber

        with pdfplumber.open(str(ruta)) as pdf:
            if not pdf.pages:
                return Documento(titulo=ruta.stem, secciones=[])

            # 1. Detectar headers/footers por repetición entre páginas
            textos_header, textos_footer = _detectar_headers_footers(pdf.pages)

            # 2. Detectar si las primeras páginas son un índice/TOC
            paginas_toc = _detectar_paginas_toc(pdf.pages[:10])

            # 3. Extraer líneas limpias de cada página
            lineas_todas: list[dict] = []
            for i, pagina in enumerate(pdf.pages):
                if i in paginas_toc:
                    continue
                altura = pagina.height or 1
                palabras = pagina.extract_words(
                    extra_attrs=["size", "fontname"],
                    keep_blank_chars=False,
                    x_tolerance=3,
                    y_tolerance=3,
                )
                lineas_pag = _agrupar_lineas(palabras)
                for linea in lineas_pag:
                    texto = linea["texto"].strip()
                    if not texto:
                        continue
                    # Descartar header/footer por posición
                    top_rel = linea.get("top", 0) / altura
                    if top_rel < _ZONA_HEADER and _normalizar(texto) in textos_header:
                        continue
                    if top_rel > _ZONA_FOOTER and _normalizar(texto) in textos_footer:
                        continue
                    # Descartar números de página
                    if _RE_SOLO_NUMERO.match(texto) or _RE_PAGINA.match(texto):
                        continue
                    # Descartar líneas decorativas
                    if _RE_SOLO_DECORATIVO.match(texto):
                        continue
                    # Descartar líneas de índice
                    if _RE_TOC_LINEA.match(texto):
                        continue
                    lineas_todas.append(linea)

        # 4. Reconstruir párrafos (unir líneas fragmentadas)
        bloques_crudos = _reconstruir_parrafos(lineas_todas)

        # 5. Estructurar en secciones
        secciones = _estructurar(bloques_crudos, ruta.stem)

        return Documento(titulo=ruta.stem, secciones=secciones)


# ── Detección de headers/footers ────────────────────────────────────────────

def _detectar_headers_footers(paginas) -> tuple[set[str], set[str]]:
    """Detecta textos que se repiten en zona top/bottom de múltiples páginas."""
    conteo_header: Counter = Counter()
    conteo_footer: Counter = Counter()

    for pagina in paginas:
        altura = pagina.height or 1
        palabras = pagina.extract_words(extra_attrs=["size"], keep_blank_chars=False)
        lineas = _agrupar_lineas(palabras)
        vistos_pag: set[str] = set()
        for linea in lineas:
            texto_norm = _normalizar(linea["texto"])
            if not texto_norm or texto_norm in vistos_pag:
                continue
            top_rel = linea.get("top", 0) / altura
            if top_rel < _ZONA_HEADER:
                conteo_header[texto_norm] += 1
                vistos_pag.add(texto_norm)
            elif top_rel > _ZONA_FOOTER:
                conteo_footer[texto_norm] += 1
                vistos_pag.add(texto_norm)

    headers = {t for t, c in conteo_header.items() if c >= _MIN_REPETICIONES_HEADER}
    footers = {t for t, c in conteo_footer.items() if c >= _MIN_REPETICIONES_HEADER}
    return headers, footers


def _normalizar(texto: str) -> str:
    """Normaliza texto para comparación: minúsculas, sin espacios extra."""
    return re.sub(r"\s+", " ", texto.lower().strip())


# ── Detección de páginas TOC ─────────────────────────────────────────────────

def _detectar_paginas_toc(paginas) -> set[int]:
    """Devuelve índices de páginas que parecen ser un índice/TOC."""
    toc_pages: set[int] = set()
    en_toc = False

    for i, pagina in enumerate(paginas):
        palabras = pagina.extract_words(extra_attrs=["size"], keep_blank_chars=False)
        lineas = _agrupar_lineas(palabras)
        textos = [l["texto"].strip() for l in lineas if l["texto"].strip()]

        if not textos:
            continue

        # Detectar título de TOC en primera línea
        if re.search(r"(?:índice|indice|contenido|table of contents|sumario)", textos[0], re.IGNORECASE):
            en_toc = True

        if en_toc:
            # Contar líneas con patrón TOC
            lineas_toc = sum(1 for t in textos if _RE_TOC_LINEA.match(t))
            if lineas_toc >= len(textos) * 0.3:
                toc_pages.add(i)
            else:
                en_toc = False  # fin del TOC

    return toc_pages


# ── Agrupación de palabras en líneas ────────────────────────────────────────

def _agrupar_lineas(palabras: list[dict]) -> list[dict]:
    if not palabras:
        return []

    lineas: list[dict] = []
    grupo: list[dict] = [palabras[0]]

    for palabra in palabras[1:]:
        top_actual = palabra.get("top", 0)
        top_ultimo = grupo[-1].get("top", 0)
        if abs(top_actual - top_ultimo) < 4:
            grupo.append(palabra)
        else:
            lineas.append(_construir_linea(grupo))
            grupo = [palabra]

    if grupo:
        lineas.append(_construir_linea(grupo))

    return lineas


def _construir_linea(palabras: list[dict]) -> dict:
    texto = " ".join(p.get("text", "") for p in palabras).translate(_LIGATURES)
    tamanos = [p.get("size", 0) for p in palabras if p.get("size")]
    tamano = max(tamanos) if tamanos else 0
    top = palabras[0].get("top", 0) if palabras else 0
    es_titulo = tamano >= _UMBRAL_TITULO_PT
    return {"texto": texto, "tamano": tamano, "es_titulo": es_titulo, "top": top}


# ── Reconstrucción de párrafos ───────────────────────────────────────────────

def _reconstruir_parrafos(lineas: list[dict]) -> list[dict]:
    """
    Une líneas fragmentadas en párrafos reales.
    Heurísticas:
    - Si la línea termina con guión → une sin espacio (palabra cortada)
    - Si la línea NO termina con puntuación final Y la siguiente empieza
      con minúscula → misma frase, unir con espacio
    - Si hay un salto de tamaño de fuente o la línea es un título → nuevo bloque
    """
    if not lineas:
        return []

    bloques: list[dict] = []
    acumulado = lineas[0].copy()

    for linea in lineas[1:]:
        texto_prev = acumulado["texto"].strip()
        texto_sig = linea["texto"].strip()

        if not texto_sig:
            continue

        # Cambio de título → siempre nuevo bloque
        if linea["es_titulo"] != acumulado["es_titulo"]:
            if texto_prev:
                bloques.append(acumulado)
            acumulado = linea.copy()
            continue

        # Cambio significativo de tamaño de fuente → nuevo bloque
        if abs(linea["tamano"] - acumulado["tamano"]) > 2:
            if texto_prev:
                bloques.append(acumulado)
            acumulado = linea.copy()
            continue

        # Línea termina con guión (palabra partida)
        if _RE_GUION_FINAL.search(texto_prev):
            acumulado["texto"] = texto_prev[:-1] + texto_sig
            continue

        # Línea termina con puntuación final → nuevo párrafo
        if _RE_FIN_PARRAFO.search(texto_prev):
            bloques.append(acumulado)
            acumulado = linea.copy()
            continue

        # Línea siguiente empieza con mayúscula después de punto implícito
        # o es muy corta (título de subsección) → nuevo bloque
        if len(texto_prev) < 60 and texto_sig and texto_sig[0].isupper():
            bloques.append(acumulado)
            acumulado = linea.copy()
            continue

        # Siguiente comienza con minúscula o es continuación → unir
        acumulado["texto"] = texto_prev + " " + texto_sig

    if acumulado["texto"].strip():
        bloques.append(acumulado)

    return bloques


# ── Estructuración en secciones ──────────────────────────────────────────────

def _estructurar(bloques: list[dict], nombre_doc: str) -> list[Seccion]:
    secciones: list[Seccion] = []
    sec_actual = Seccion(titulo=nombre_doc, nivel=0, bloques=[])

    for bloque in bloques:
        texto = bloque["texto"].strip()
        if not texto:
            continue

        if bloque["es_titulo"]:
            nivel = 1 if bloque["tamano"] >= _UMBRAL_TITULO_PT + 4 else 2
            if sec_actual.bloques or sec_actual.titulo != nombre_doc:
                secciones.append(sec_actual)
            sec_actual = Seccion(titulo=texto, nivel=nivel, bloques=[])
            continue

        # Detectar lista
        m_lista = _RE_LISTA.match(texto) or _RE_LISTA_NUM.match(texto)
        if m_lista:
            item = m_lista.group(1).strip()
            if sec_actual.bloques and sec_actual.bloques[-1].tipo == TipoBloque.LISTA:
                sec_actual.bloques[-1].items_lista.append(item)
            else:
                sec_actual.bloques.append(Bloque(tipo=TipoBloque.LISTA, items_lista=[item]))
            continue

        sec_actual.bloques.append(Bloque(tipo=TipoBloque.PARRAFO, contenido=texto))

    if sec_actual.bloques or sec_actual.titulo != nombre_doc:
        secciones.append(sec_actual)

    if not secciones:
        secciones.append(Seccion(titulo=nombre_doc, nivel=1, bloques=[]))

    return secciones
