"""
Lector PDF con 9 mejoras estructurales:
1. Headers/footers por repetición (no por cm)
2. Números de página eliminados
3. Índices/TOC detectados y omitidos
4. Párrafos reconstruidos (no una línea por línea de PDF)
5. Columnas múltiples: se leen por columna, no mezcladas
6. Continuidad entre páginas: párrafo que corta en salto de página se une
7. Notas al pie: detectadas y separadas del flujo principal
8. Tablas: extraídas con estructura real de filas/columnas
9. Pies de figura/tabla: identificados como CAPTION
10. Negrita/cursiva: detectados por fontname
11. Metadatos del PDF: título, autor, fecha
12. PDFs escaneados: fallback OCR con pytesseract si disponible
13. Detección de idioma automática
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from txt2media.core.modelo import (
    Bloque, Documento, FilaTabla, Seccion, Tabla, TipoBloque,
)

# ── Umbrales ─────────────────────────────────────────────────────────────────
_UMBRAL_TITULO_PT  = 14.0
_MIN_REPS_HEADER   = 3
_ZONA_HEADER       = 0.10
_ZONA_FOOTER       = 0.90
_UMBRAL_NOTA_PIE   = 9.0   # fuente pequeña = nota al pie
_UMBRAL_OCR_WORDS  = 5     # menos palabras = página escaneada

# ── Patrones ─────────────────────────────────────────────────────────────────
_RE_NUM_PAG   = re.compile(r"^\s*[\-–—·•]?\s*\d+\s*[\-–—·•]?\s*$")
_RE_PAG_TEXTO = re.compile(
    r"^\s*(?:página|page|pág\.?|p\.?)?\s*\d+\s*(?:de|of|/\s*\d+)?\s*$",
    re.IGNORECASE,
)
_RE_DECORATIVO = re.compile(r"^[\-–—_=\*\.·•\s]{3,}$")
_RE_TOC_LINEA  = re.compile(r"^.{2,}[\.\s]{4,}\d{1,4}\s*$")
_RE_CAPTION    = re.compile(
    r"^\s*(?:figura|figure|fig\.|gráfico|grafico|tabla|table|cuadro|imagen|image)"
    r"\s*\d*[\.\:\-]",
    re.IGNORECASE,
)
_RE_NOTA_MARCA = re.compile(r"^\s*[\d¹²³⁴⁵⁶⁷⁸⁹\*†‡§]\s+\S")
_RE_FIN_PARRAF = re.compile(r"[.!?]\s*$")
_RE_GUION_CORTE = re.compile(r"-$")

# Ligaduras tipográficas
_LIGATURES = str.maketrans({
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
    "ﬁ": "fi", "ﬂ": "fl", "­": "",
})

# Palabras clave por idioma para detección
_PALABRAS_ES = {"de", "la", "el", "en", "que", "y", "los", "las", "del", "con", "por", "se"}
_PALABRAS_EN = {"the", "of", "and", "to", "in", "is", "that", "for", "it", "with", "as", "at"}


# ═══════════════════════════════════════════════════════════════════════════
class LectorPDF:
    def leer(self, ruta: Path) -> Documento:
        import pdfplumber

        with pdfplumber.open(str(ruta)) as pdf:
            if not pdf.pages:
                return Documento(titulo=ruta.stem, secciones=[])

            # ── Metadatos ───────────────────────────────────────────────
            meta   = pdf.metadata or {}
            titulo = _limpiar_meta(meta.get("Title") or meta.get("title") or "") or ruta.stem
            autor  = _limpiar_meta(meta.get("Author") or meta.get("author") or "")

            # ── Headers/footers por repetición ──────────────────────────
            textos_hdr, textos_ftr = _detectar_headers_footers(pdf.pages)

            # ── Páginas de TOC ───────────────────────────────────────────
            paginas_toc = _detectar_paginas_toc(pdf.pages[:12])

            # ── Extraer bloques página a página ─────────────────────────
            bloques_por_pag: list[list[dict]] = []
            notas_pie_globales: list[str] = []

            for idx, pagina in enumerate(pdf.pages):
                if idx in paginas_toc:
                    continue
                altura = pagina.height or 1

                # Tablas primero (pdfplumber)
                tablas_pag = _extraer_tablas(pagina)

                # Palabras de texto
                palabras = pagina.extract_words(
                    extra_attrs=["size", "fontname"],
                    keep_blank_chars=False,
                    x_tolerance=3,
                    y_tolerance=3,
                )

                # OCR fallback si página sin texto
                if len(palabras) < _UMBRAL_OCR_WORDS:
                    palabras = _ocr_fallback(pagina)

                if not palabras and not tablas_pag:
                    continue

                # Detectar columnas
                columnas = _detectar_columnas(palabras, pagina.width or 600)

                lineas_pag: list[dict] = []
                notas_pag: list[str] = []

                for col_palabras in columnas:
                    lineas_col = _agrupar_lineas(col_palabras)
                    for linea in lineas_col:
                        texto = linea["texto"].strip()
                        if not texto:
                            continue
                        top_rel = linea.get("top", 0) / altura

                        # Filtrar header/footer por posición + repetición
                        if top_rel < _ZONA_HEADER and _norm(texto) in textos_hdr:
                            continue
                        if top_rel > _ZONA_FOOTER and _norm(texto) in textos_ftr:
                            continue
                        # Número de página
                        if _RE_NUM_PAG.match(texto) or _RE_PAG_TEXTO.match(texto):
                            continue
                        # Decorativo
                        if _RE_DECORATIVO.match(texto):
                            continue
                        # TOC inline
                        if _RE_TOC_LINEA.match(texto):
                            continue
                        # Nota al pie (fuente pequeña + marca)
                        if linea["tamano"] <= _UMBRAL_NOTA_PIE and _RE_NOTA_MARCA.match(texto):
                            notas_pag.append(texto)
                            continue

                        lineas_pag.append(linea)

                notas_pie_globales.extend(notas_pag)

                # Insertar tablas en posición correcta
                bloques_pag = _lineas_a_bloques(lineas_pag, tablas_pag, altura)
                bloques_por_pag.append(bloques_pag)

            # ── Continuidad entre páginas ────────────────────────────────
            bloques_todos = _unir_paginas(bloques_por_pag)

            # ── Reconstruir párrafos dentro de cada página ───────────────
            bloques_todos = _reconstruir_parrafos(bloques_todos)

            # ── Estructurar en secciones ─────────────────────────────────
            secciones = _estructurar(bloques_todos, titulo)

        # ── Detección de idioma ──────────────────────────────────────────
        idioma = _detectar_idioma(secciones)

        return Documento(
            titulo=titulo,
            autor=autor,
            idioma=idioma,
            secciones=secciones,
            metadatos={k: v for k, v in meta.items() if isinstance(v, str)},
        )


# ═══════════════════════════════════════════════════════════════════════════
# Metadatos
# ═══════════════════════════════════════════════════════════════════════════

def _limpiar_meta(valor: str) -> str:
    if not valor:
        return ""
    # Eliminar encoding BOM y caracteres de control
    return re.sub(r"[\x00-\x1f]+", " ", valor).strip()


# ═══════════════════════════════════════════════════════════════════════════
# Headers / footers
# ═══════════════════════════════════════════════════════════════════════════

def _detectar_headers_footers(paginas) -> tuple[set[str], set[str]]:
    conteo_hdr: Counter = Counter()
    conteo_ftr: Counter = Counter()

    for pagina in paginas:
        altura = pagina.height or 1
        palabras = pagina.extract_words(extra_attrs=["size"], keep_blank_chars=False)
        lineas = _agrupar_lineas(palabras)
        vistos: set[str] = set()
        for linea in lineas:
            tn = _norm(linea["texto"])
            if not tn or tn in vistos:
                continue
            top_rel = linea.get("top", 0) / altura
            if top_rel < _ZONA_HEADER:
                conteo_hdr[tn] += 1
                vistos.add(tn)
            elif top_rel > _ZONA_FOOTER:
                conteo_ftr[tn] += 1
                vistos.add(tn)

    hdrs = {t for t, c in conteo_hdr.items() if c >= _MIN_REPS_HEADER}
    ftrs = {t for t, c in conteo_ftr.items() if c >= _MIN_REPS_HEADER}
    return hdrs, ftrs


def _norm(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.lower().strip())


# ═══════════════════════════════════════════════════════════════════════════
# TOC
# ═══════════════════════════════════════════════════════════════════════════

def _detectar_paginas_toc(paginas) -> set[int]:
    toc: set[int] = set()
    en_toc = False
    for i, pagina in enumerate(paginas):
        palabras = pagina.extract_words(extra_attrs=["size"], keep_blank_chars=False)
        lineas = _agrupar_lineas(palabras)
        textos = [l["texto"].strip() for l in lineas if l["texto"].strip()]
        if not textos:
            continue
        if re.search(r"(?:índice|indice|contenido|table of contents|sumario)", textos[0], re.I):
            en_toc = True
        if en_toc:
            n_toc = sum(1 for t in textos if _RE_TOC_LINEA.match(t))
            if n_toc >= len(textos) * 0.3:
                toc.add(i)
            else:
                en_toc = False
    return toc


# ═══════════════════════════════════════════════════════════════════════════
# Columnas múltiples
# ═══════════════════════════════════════════════════════════════════════════

def _detectar_columnas(palabras: list[dict], ancho_pagina: float) -> list[list[dict]]:
    """Divide palabras en columnas detectando huecos horizontales significativos."""
    if not palabras:
        return [[]]

    # Histograma de ocupación horizontal (resolución: 10 px)
    slot = max(1, int(ancho_pagina / 100))
    ocup = [0] * (int(ancho_pagina / slot) + 2)
    for p in palabras:
        x0 = int(p.get("x0", 0) / slot)
        x1 = int(p.get("x1", p.get("x0", 0)) / slot) + 1
        for x in range(max(0, x0), min(len(ocup), x1)):
            ocup[x] += 1

    # Encontrar huecos (zonas vacías ≥ 3% del ancho)
    umbral_hueco = max(3, int(ancho_pagina * 0.03 / slot))
    separadores: list[float] = []
    en_hueco = False
    inicio_hueco = 0
    for x, v in enumerate(ocup):
        if v == 0 and not en_hueco:
            en_hueco = True
            inicio_hueco = x
        elif v > 0 and en_hueco:
            en_hueco = False
            if (x - inicio_hueco) >= umbral_hueco:
                sep_px = (inicio_hueco + x) / 2 * slot
                # Solo separadores en zona central (10%–90% del ancho)
                if ancho_pagina * 0.1 < sep_px < ancho_pagina * 0.9:
                    separadores.append(sep_px)

    if not separadores:
        return [palabras]

    # Asignar cada palabra a su columna
    limites = [0.0] + separadores + [ancho_pagina + 1]
    columnas: list[list[dict]] = [[] for _ in range(len(limites) - 1)]
    for p in palabras:
        cx = p.get("x0", 0)
        for col_idx in range(len(limites) - 1):
            if limites[col_idx] <= cx < limites[col_idx + 1]:
                columnas[col_idx].append(p)
                break

    return [c for c in columnas if c]


# ═══════════════════════════════════════════════════════════════════════════
# Tablas
# ═══════════════════════════════════════════════════════════════════════════

def _extraer_tablas(pagina) -> list[dict]:
    """Extrae tablas de pdfplumber con su posición en la página."""
    tablas = []
    try:
        for t in pagina.find_tables():
            datos = t.extract()
            if not datos:
                continue
            bbox = t.bbox  # (x0, top, x1, bottom)
            filas: list[FilaTabla] = []
            encabezados: list[str] = []
            for i, fila in enumerate(datos):
                celdas = [str(c or "").strip() for c in fila]
                if i == 0:
                    encabezados = celdas
                    filas.append(FilaTabla(celdas=celdas, es_encabezado=True))
                else:
                    filas.append(FilaTabla(celdas=celdas))
            tablas.append({
                "top": bbox[1],
                "tabla": Tabla(encabezados=encabezados, filas=filas),
            })
    except Exception:
        pass
    return tablas


# ═══════════════════════════════════════════════════════════════════════════
# OCR fallback
# ═══════════════════════════════════════════════════════════════════════════

def _ocr_fallback(pagina) -> list[dict]:
    """Intenta OCR con pytesseract si la página no tiene texto."""
    try:
        import pytesseract
        from PIL import Image
        import io

        img_bytes = pagina.to_image(resolution=150).original
        if hasattr(img_bytes, "tobytes"):
            # Es objeto PIL
            img = img_bytes
        else:
            img = Image.open(io.BytesIO(img_bytes))

        texto = pytesseract.image_to_string(img, lang="spa+eng")
        # Convertir a formato similar a extract_words
        palabras = []
        for linea in texto.split("\n"):
            for pal in linea.split():
                palabras.append({"text": pal, "size": 11.0, "fontname": "OCR",
                                 "top": 0, "x0": 0, "x1": 0})
        return palabras
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════
# Agrupación de palabras en líneas
# ═══════════════════════════════════════════════════════════════════════════

def _agrupar_lineas(palabras: list[dict]) -> list[dict]:
    if not palabras:
        return []
    lineas: list[dict] = []
    grupo: list[dict] = [palabras[0]]
    for p in palabras[1:]:
        if abs(p.get("top", 0) - grupo[-1].get("top", 0)) < 4:
            grupo.append(p)
        else:
            lineas.append(_construir_linea(grupo))
            grupo = [p]
    if grupo:
        lineas.append(_construir_linea(grupo))
    return lineas


def _construir_linea(palabras: list[dict]) -> dict:
    texto = " ".join(p.get("text", "") for p in palabras).translate(_LIGATURES)
    tamanos = [p.get("size", 0) for p in palabras if p.get("size")]
    tamano = max(tamanos) if tamanos else 0
    top = palabras[0].get("top", 0) if palabras else 0
    # Detectar negrita/cursiva por fontname
    nombres = " ".join(p.get("fontname", "") for p in palabras).lower()
    negrita = "bold" in nombres
    cursiva  = "italic" in nombres or "oblique" in nombres
    return {
        "texto": texto,
        "tamano": tamano,
        "es_titulo": tamano >= _UMBRAL_TITULO_PT,
        "top": top,
        "negrita": negrita,
        "cursiva": cursiva,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Lineas + tablas → bloques crudos con posición
# ═══════════════════════════════════════════════════════════════════════════

def _lineas_a_bloques(lineas: list[dict], tablas: list[dict], altura: float) -> list[dict]:
    """Mezcla líneas de texto y tablas ordenadas por posición vertical."""
    items: list[dict] = []
    for linea in lineas:
        items.append({"tipo": "linea", "top": linea["top"], "datos": linea})
    for t in tablas:
        items.append({"tipo": "tabla", "top": t["top"], "datos": t["tabla"]})
    items.sort(key=lambda x: x["top"])
    return items


# ═══════════════════════════════════════════════════════════════════════════
# Continuidad entre páginas
# ═══════════════════════════════════════════════════════════════════════════

def _unir_paginas(paginas: list[list[dict]]) -> list[dict]:
    """Une bloques de todas las páginas y pega párrafos que cruzan salto."""
    if not paginas:
        return []

    resultado: list[dict] = list(paginas[0])

    for pag in paginas[1:]:
        if not pag:
            continue
        # Intentar unir último bloque de página anterior con primer bloque de esta
        if (resultado and pag and
                resultado[-1].get("tipo") == "linea" and
                pag[0].get("tipo") == "linea"):
            ultimo = resultado[-1]["datos"]
            primero = pag[0]["datos"]
            texto_u = ultimo["texto"].strip()
            texto_p = primero["texto"].strip()
            # Unir si: último no termina en puntuación Y no es título Y primero empieza en minúscula
            if (not ultimo.get("es_titulo") and
                    not primero.get("es_titulo") and
                    not _RE_FIN_PARRAF.search(texto_u) and
                    texto_p and texto_p[0].islower()):
                if _RE_GUION_CORTE.search(texto_u):
                    ultimo["texto"] = texto_u[:-1] + texto_p
                else:
                    ultimo["texto"] = texto_u + " " + texto_p
                resultado.extend(pag[1:])
                continue

        resultado.extend(pag)

    return resultado


# ═══════════════════════════════════════════════════════════════════════════
# Reconstrucción de párrafos
# ═══════════════════════════════════════════════════════════════════════════

def _reconstruir_parrafos(items: list[dict]) -> list[dict]:
    if not items:
        return []

    resultado: list[dict] = []
    acum: dict | None = None

    for item in items:
        if item["tipo"] == "tabla":
            if acum:
                resultado.append(acum)
                acum = None
            resultado.append(item)
            continue

        linea = item["datos"]
        texto = linea["texto"].strip()
        if not texto:
            continue

        if acum is None:
            acum = dict(item)
            continue

        texto_prev = acum["datos"]["texto"].strip()
        linea_prev = acum["datos"]

        # Cambio de tipo (título vs párrafo) → nuevo bloque
        if linea.get("es_titulo") != linea_prev.get("es_titulo"):
            resultado.append(acum)
            acum = dict(item)
            continue

        # Cambio de tamaño > 2pt → nuevo bloque
        if abs(linea.get("tamano", 0) - linea_prev.get("tamano", 0)) > 2:
            resultado.append(acum)
            acum = dict(item)
            continue

        # Termina con guión (palabra partida) → unir sin espacio
        if _RE_GUION_CORTE.search(texto_prev):
            acum["datos"] = dict(linea_prev)
            acum["datos"]["texto"] = texto_prev[:-1] + texto
            continue

        # Termina con puntuación final → nuevo párrafo
        if _RE_FIN_PARRAF.search(texto_prev):
            resultado.append(acum)
            acum = dict(item)
            continue

        # Línea corta + siguiente en mayúscula → nuevo bloque (título implícito)
        if len(texto_prev) < 60 and texto and texto[0].isupper():
            resultado.append(acum)
            acum = dict(item)
            continue

        # Siguiente en minúscula → misma frase, unir
        acum["datos"] = dict(linea_prev)
        acum["datos"]["texto"] = texto_prev + " " + texto

    if acum:
        resultado.append(acum)

    return resultado


# ── Patrones de lista (deben estar antes de _estructurar) ────────────────────
_RE_LISTA     = re.compile(r"^[•○▪▸→►◆\-\*]\s+(.+)$")
_RE_LISTA_NUM = re.compile(r"^\d{1,2}[.)]\s+(.+)$")

# ═══════════════════════════════════════════════════════════════════════════
# Estructuración en secciones
# ═══════════════════════════════════════════════════════════════════════════

def _estructurar(items: list[dict], nombre_doc: str) -> list[Seccion]:
    secciones: list[Seccion] = []
    sec_actual = Seccion(titulo=nombre_doc, nivel=0, bloques=[])

    for item in items:
        if item["tipo"] == "tabla":
            tabla: Tabla = item["datos"]
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.TABLA, tabla=tabla))
            continue

        linea = item["datos"]
        texto = linea["texto"].strip()
        if not texto:
            continue

        negrita = linea.get("negrita", False)
        cursiva  = linea.get("cursiva", False)

        # Caption (pie de figura/tabla)
        if _RE_CAPTION.match(texto):
            sec_actual.bloques.append(
                Bloque(tipo=TipoBloque.CAPTION, contenido=texto)
            )
            continue

        # Título → nueva sección
        if linea.get("es_titulo"):
            nivel = 1 if linea.get("tamano", 0) >= _UMBRAL_TITULO_PT + 4 else 2
            if sec_actual.bloques or sec_actual.titulo != nombre_doc:
                secciones.append(sec_actual)
            sec_actual = Seccion(titulo=texto, nivel=nivel, bloques=[])
            continue

        # Lista
        m = _RE_LISTA.match(texto) or _RE_LISTA_NUM.match(texto)
        if m:
            item_txt = m.group(1).strip()
            if sec_actual.bloques and sec_actual.bloques[-1].tipo == TipoBloque.LISTA:
                sec_actual.bloques[-1].items_lista.append(item_txt)
            else:
                sec_actual.bloques.append(Bloque(tipo=TipoBloque.LISTA, items_lista=[item_txt]))
            continue

        sec_actual.bloques.append(
            Bloque(tipo=TipoBloque.PARRAFO, contenido=texto,
                   negrita=negrita, cursiva=cursiva)
        )

    if sec_actual.bloques or sec_actual.titulo != nombre_doc:
        secciones.append(sec_actual)

    if not secciones:
        secciones.append(Seccion(titulo=nombre_doc, nivel=1, bloques=[]))

    return secciones


# ═══════════════════════════════════════════════════════════════════════════
# Detección de idioma
# ═══════════════════════════════════════════════════════════════════════════

def _detectar_idioma(secciones: list[Seccion]) -> str:
    palabras: list[str] = []
    for sec in secciones[:5]:
        for bloque in sec.bloques[:3]:
            if bloque.tipo == TipoBloque.PARRAFO:
                palabras.extend(bloque.contenido.lower().split()[:20])
        if len(palabras) > 60:
            break

    muestra = set(palabras)
    hits_es = len(muestra & _PALABRAS_ES)
    hits_en = len(muestra & _PALABRAS_EN)

    if hits_en > hits_es * 1.5:
        return "en"
    return "es"
