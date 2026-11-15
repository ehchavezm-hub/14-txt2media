"""Generador HTML enriquecido con menú lateral y tema Tableau."""

from __future__ import annotations

import re
from pathlib import Path

from txt2media.core.modelo import Documento, TipoBloque

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Figtree', 'Segoe UI', Arial, sans-serif;
    background: #F5F5F5;
    color: #1A1A1A;
    display: flex;
    min-height: 100vh;
}
#sidebar {
    width: 280px;
    min-width: 220px;
    background: #1E1E1E;
    color: #F5F5F5;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    overflow-y: auto;
    padding: 24px 0;
    z-index: 100;
}
#sidebar .brand {
    color: #4E79A7;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 0 20px 16px;
    border-bottom: 1px solid #333;
    margin-bottom: 12px;
}
#sidebar nav a {
    display: block;
    padding: 8px 20px;
    color: #CCCCCC;
    text-decoration: none;
    font-size: 0.85rem;
    border-left: 3px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#sidebar nav a:hover, #sidebar nav a.activo {
    color: #FFFFFF;
    background: #2A2A2A;
    border-left-color: #F28E2B;
}
#main {
    margin-left: 280px;
    flex: 1;
    padding: 40px 48px;
    max-width: 900px;
}
#portada {
    background: linear-gradient(135deg, #4E79A7 0%, #2E5A8A 100%);
    color: white;
    padding: 48px;
    border-radius: 8px;
    margin-bottom: 40px;
}
#portada h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
#portada .meta { opacity: 0.75; font-size: 0.95rem; }
.seccion {
    background: white;
    border-radius: 8px;
    padding: 32px 36px;
    margin-bottom: 24px;
    border-left: 4px solid #4E79A7;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    scroll-margin-top: 24px;
}
.seccion h2 {
    color: #4E79A7;
    font-size: 1.3rem;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #EEE;
}
.seccion p { line-height: 1.75; margin-bottom: 12px; color: #333; }
.seccion p:last-child { margin-bottom: 0; }
.seccion ul { margin: 8px 0 12px 20px; }
.seccion ul li { line-height: 1.7; color: #333; margin-bottom: 4px; }
.caption { color: #888; font-size: 0.85rem; font-style: italic; margin: -4px 0 12px; }
.tabla-wrap { overflow-x: auto; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
th { background: #4E79A7; color: white; padding: 8px 12px; text-align: left; }
td { border: 1px solid #DDD; padding: 7px 12px; }
tr:nth-child(even) td { background: #F8F8F8; }
.tag-sigla { background: #FFF3E0; color: #F28E2B; font-weight: 700;
             padding: 1px 4px; border-radius: 3px; font-size: 0.9em; }
.tag-num   { color: #59A14F; font-weight: 700; }
html { scroll-behavior: smooth; }
@media (max-width: 768px) {
    #sidebar { display: none; }
    #main { margin-left: 0; padding: 20px; }
}
"""

_JS = """
const secciones = document.querySelectorAll('.seccion');
const links = document.querySelectorAll('#sidebar nav a');
function marcarActivo() {
    let activo = null;
    secciones.forEach(s => { if (s.getBoundingClientRect().top <= 80) activo = s.id; });
    links.forEach(a => a.classList.toggle('activo', a.getAttribute('href') === '#' + activo));
}
window.addEventListener('scroll', marcarActivo, { passive: true });
marcarActivo();
"""


class GeneradorHTML:
    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        salida.parent.mkdir(parents=True, exist_ok=True)
        html = self._construir(doc)
        tmp = salida.with_suffix(".tmp")
        tmp.write_text(html, encoding="utf-8")
        import os
        os.replace(str(tmp), str(salida))
        return salida

    def _construir(self, doc: Documento) -> str:
        nav_items = []
        secciones_html = []

        for i, sec in enumerate(doc.secciones, 1):
            titulo = sec.titulo or f"Sección {i}"
            sid = f"sec-{i}"
            nav_items.append(f'<a href="#{sid}">{i}. {self._esc(titulo)}</a>')

            bloques_html = []
            for bloque in sec.bloques:
                if bloque.tipo == TipoBloque.PARRAFO:
                    t = self._enriquecer(bloque.contenido.strip())
                    if bloque.negrita and bloque.cursiva:
                        t = f"<strong><em>{t}</em></strong>"
                    elif bloque.negrita:
                        t = f"<strong>{t}</strong>"
                    elif bloque.cursiva:
                        t = f"<em>{t}</em>"
                    bloques_html.append(f"<p>{t}</p>")

                elif bloque.tipo == TipoBloque.LISTA:
                    items = "".join(f"<li>{self._enriquecer(it)}</li>" for it in bloque.items_lista)
                    bloques_html.append(f"<ul>{items}</ul>")

                elif bloque.tipo == TipoBloque.CAPTION:
                    bloques_html.append(f'<p class="caption">{self._esc(bloque.contenido)}</p>')

                elif bloque.tipo == TipoBloque.TABLA and bloque.tabla:
                    t = bloque.tabla
                    filas_html = ""
                    for fila in t.filas:
                        tag = "th" if fila.es_encabezado else "td"
                        celdas = "".join(f"<{tag}>{self._esc(c)}</{tag}>" for c in fila.celdas)
                        filas_html += f"<tr>{celdas}</tr>"
                    bloques_html.append(f'<div class="tabla-wrap"><table>{filas_html}</table></div>')

            secciones_html.append(
                f'<section class="seccion" id="{sid}">'
                f'<h2>{self._esc(titulo)}</h2>'
                + "".join(bloques_html) +
                f'</section>'
            )

        titulo_esc = self._esc(doc.titulo)
        meta_linea = " · ".join(filter(None, [doc.autor, f"{len(doc.secciones)} secciones"]))

        return f"""<!DOCTYPE html>
<html lang="{doc.idioma or 'es'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo_esc}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700&display=swap" rel="stylesheet">
<style>{_CSS}</style>
</head>
<body>
<div id="sidebar">
  <div class="brand">▶ txt2media</div>
  <nav>
    <a href="#portada">Inicio</a>
    {"".join(nav_items)}
  </nav>
</div>
<div id="main">
  <div id="portada">
    <h1>{titulo_esc}</h1>
    <div class="meta">{self._esc(meta_linea)}</div>
  </div>
  {"".join(secciones_html)}
</div>
<script>{_JS}</script>
</body>
</html>"""

    def _esc(self, t: str) -> str:
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _enriquecer(self, texto: str) -> str:
        texto = self._esc(texto)
        texto = re.sub(r"\b([A-Z]{2,})\b", r'<span class="tag-sigla">\1</span>', texto)
        texto = re.sub(r"\b(\d+[\.,]?\d*\s*%)", r'<span class="tag-num">\1</span>', texto)
        return texto
