"""Generador Markdown: limpio, legible en cualquier visor (MarkText, GitHub, VS Code, Obsidian).

Usa solo Markdown estándar (GFM) y el poco HTML que todos los visores muestran
(`<div align="center">`), en vez de estilos en línea que la mayoría descarta.
"""

from __future__ import annotations

import base64
import os
import re
import tempfile
from datetime import date
from pathlib import Path

from txt2media.core.modelo import Bloque, Documento, TipoBloque
from txt2media.generadores.estilo import (
    _RE_PORCENTAJE, formato_miles, minutos_lectura, nivel_relativo, numeracion, palabras_de, slug_github,
)

_RE_NUM_TITULO = re.compile(r"^\s*(\d+(?:\.\d+)*)[.)]?\s+(\S.*)$")
_RE_INICIO_ESPECIAL = re.compile(r"^(\s*)(#|>|[-+*]\s|\d+[.)]\s|=+\s*$|-{3,}\s*$)")
_MAX_IMAGEN = 300_000  # bytes: imágenes más grandes no se incrustan


def _texto(t: str) -> str:
    """Escapa lo que Markdown interpretaría como estructura o HTML."""
    t = (t or "").replace("\r", "").strip()
    t = t.replace("<", "&lt;").replace(">", "&gt;") if "<" in t else t
    lineas = []
    for linea in t.split("\n"):
        linea = _RE_INICIO_ESPECIAL.sub(lambda m: m.group(1) + "\\" + m.group(2), linea)
        lineas.append(linea)
    return "\n".join(lineas)


def _celda(t: str) -> str:
    return _texto(t).replace("|", "\\|").replace("\n", " ")


def _enriquecer(t: str) -> str:
    return _RE_PORCENTAJE.sub(r"**\1**", _texto(t))


class GeneradorMD:
    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        contenido = self._construir(doc)
        fd, tmp = tempfile.mkstemp(suffix=".md", dir=salida.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(contenido)
            os.chmod(tmp, 0o644)  # mkstemp crea el archivo solo para el dueño
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return salida

    def _construir(self, doc: Documento) -> str:
        secciones = doc.secciones
        numeros = numeracion(secciones)
        palabras = palabras_de(doc)
        titulo = (doc.titulo or "Documento").strip()
        hoy = date.today().isoformat()
        L: list[str] = []

        # Ficha (front matter): la leen Obsidian, MarkText, Pandoc y generadores de sitios
        L += ["---", f'title: "{titulo.replace(chr(34), chr(39))}"']
        if doc.autor:
            L.append(f'author: "{doc.autor.replace(chr(34), chr(39))}"')
        L += [f"date: {hoy}", f"lang: {doc.idioma or 'es'}", "generator: txt2media", "---", ""]

        # Cabecera
        L += ['<div align="center">', "", f"# {_texto(titulo)}", ""]
        if doc.autor:
            L += [f"**{_texto(doc.autor)}**", ""]
        L += [
            f"`{len(secciones)} secciones` · `{formato_miles(palabras)} palabras` · "
            f"`{minutos_lectura(palabras)} min de lectura`",
            "", "</div>", "", "---", "",
        ]

        # Encabezados finales y sus anclas (iguales a las que generan GitHub y MarkText)
        usados: dict[str, int] = {"contenido": 1}
        encabezados = []
        for i, sec in enumerate(secciones):
            nombre = (sec.titulo or f"Sección {numeros[i]}").strip()
            numero = numeros[i]
            m = _RE_NUM_TITULO.match(nombre)
            if m:
                numero, nombre = m.group(1), m.group(2)
            texto_h = f"{numero} · {nombre}"
            encabezados.append((nivel_relativo(secciones, sec), texto_h, slug_github(texto_h, usados)))

        # Índice
        L += ["## Contenido", ""]
        for nivel, texto_h, ancla in encabezados:
            sangria = "  " * (min(nivel, 3) - 1)
            L.append(f"{sangria}- [{_celda(texto_h)}](#{ancla})")
        L += ["", "---", ""]

        # Secciones
        for i, sec in enumerate(secciones):
            nivel, texto_h, _ = encabezados[i]
            L += [f"{'#' * (min(nivel, 4) + 1)} {_texto(texto_h)}", ""]
            L += self._bloques(sec.bloques)
            siguiente_es_capitulo = i + 1 >= len(secciones) or encabezados[i + 1][0] == 1
            if siguiente_es_capitulo:
                L += ['<div align="right"><a href="#contenido">↑ Volver al índice</a></div>', "", "---", ""]

        L += [f"<sub>Generado con txt2media · {hoy}</sub>", ""]
        return "\n".join(L)

    def _bloques(self, bloques: list[Bloque]) -> list[str]:
        L: list[str] = []
        notas: list[str] = []
        for b in bloques:
            t = b.tipo
            if t == TipoBloque.PARRAFO and b.contenido.strip():
                texto = _enriquecer(b.contenido)
                if b.negrita and b.cursiva:
                    texto = f"***{texto}***"
                elif b.negrita:
                    texto = f"**{texto}**"
                elif b.cursiva:
                    texto = f"*{texto}*"
                L += [texto, ""]
            elif t == TipoBloque.TITULO and b.contenido.strip():
                L += [f"#### {_texto(b.contenido)}", ""]
            elif t == TipoBloque.LISTA and b.items_lista:
                L += [f"- {_enriquecer(it)}" for it in b.items_lista] + [""]
            elif t == TipoBloque.CITA and b.contenido.strip():
                L += ["> " + linea for linea in _texto(b.contenido).split("\n")] + [""]
            elif t == TipoBloque.CODIGO and b.contenido:
                cerca = "````" if "```" in b.contenido else "```"
                L += [f"{cerca}{b.idioma_codigo or ''}", b.contenido.rstrip("\n"), cerca, ""]
            elif t == TipoBloque.TABLA and b.tabla:
                L += self._tabla(b) + [""]
            elif t == TipoBloque.IMAGEN and b.imagen:
                L += self._imagen(b)
            elif t == TipoBloque.CAPTION and b.contenido.strip():
                L += [f"<sub>{_texto(b.contenido)}</sub>", ""]
            elif t == TipoBloque.NOTA_PIE and b.contenido.strip():
                notas.append(_texto(b.contenido))
            elif t == TipoBloque.SEPARADOR:
                L += ['<div align="center">· · ·</div>', ""]
        if notas:
            L += ["> [!NOTE]", "> **Notas**"]
            for n in notas:
                L += [">", f"> {n}"]
            L.append("")
        return L

    def _tabla(self, b: Bloque) -> list[str]:
        t = b.tabla
        filas = [f.celdas for f in t.filas]
        cab = list(t.encabezados)
        if not cab:
            con_cab = [f for f in t.filas if f.es_encabezado]
            if con_cab:
                cab = con_cab[0].celdas
                filas = [f.celdas for f in t.filas if f is not con_cab[0]]
            elif filas:
                cab, filas = filas[0], filas[1:]
        n = max([len(cab)] + [len(f) for f in filas] + [0])
        if n == 0:
            return []
        cab = list(cab) + [""] * (n - len(cab))
        L = ["| " + " | ".join(_celda(c) or " " for c in cab) + " |",
             "|" + "|".join([" --- "] * n) + "|"]
        for f in filas:
            f = list(f) + [""] * (n - len(f))
            L.append("| " + " | ".join(_celda(c) for c in f) + " |")
        return L

    def _imagen(self, b: Bloque) -> list[str]:
        img = b.imagen
        datos = img.datos
        if datos is None and img.ruta and Path(img.ruta).exists():
            try:
                datos = Path(img.ruta).read_bytes()
            except OSError:
                datos = None
        if not datos or len(datos) > _MAX_IMAGEN:
            return [f"*[Imagen: {_texto(img.alt) or 'sin descripción'}]*", ""]
        tipo = "jpeg" if datos[:3] == b"\xff\xd8\xff" else "png"
        src = f"data:image/{tipo};base64,{base64.b64encode(datos).decode('ascii')}"
        return [f"![{_celda(img.alt)}]({src})", ""]
