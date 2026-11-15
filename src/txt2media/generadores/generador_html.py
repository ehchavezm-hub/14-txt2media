"""Generador HTML enriquecido con menú lateral y tema Tableau."""

from __future__ import annotations

import re
from pathlib import Path

from txt2media.core.modelo import Documento

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Figtree', 'Segoe UI', Arial, sans-serif;
    background: #F5F5F5;
    color: #1A1A1A;
    display: flex;
    min-height: 100vh;
}
/* Sidebar */
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
#sidebar h2 {
    color: #4E79A7;
    font-size: 1rem;
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
/* Main */
#main {
    margin-left: 280px;
    flex: 1;
    padding: 40px 48px;
    max-width: 900px;
}
/* Portada */
#portada {
    background: linear-gradient(135deg, #4E79A7 0%, #2E5A8A 100%);
    color: white;
    padding: 48px;
    border-radius: 8px;
    margin-bottom: 40px;
}
#portada h1 { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
#portada p { opacity: 0.8; font-size: 1rem; }
/* Secciones */
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
.seccion p {
    line-height: 1.75;
    margin-bottom: 12px;
    color: #333;
}
.seccion p:last-child { margin-bottom: 0; }
.tag-sigla {
    background: #FFF3E0;
    color: #F28E2B;
    font-weight: 700;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}
.tag-num {
    color: #59A14F;
    font-weight: 700;
}
/* Scroll suave */
html { scroll-behavior: smooth; }
/* Responsive */
@media (max-width: 768px) {
    #sidebar { display: none; }
    #main { margin-left: 0; padding: 20px; }
}
"""

_JS = """
// Resaltar sección activa en sidebar al hacer scroll
const secciones = document.querySelectorAll('.seccion');
const links = document.querySelectorAll('#sidebar nav a');
function actualizarActivo() {
    let activo = null;
    secciones.forEach(s => {
        if (s.getBoundingClientRect().top <= 80) activo = s.id;
    });
    links.forEach(a => {
        a.classList.toggle('activo', a.getAttribute('href') === '#' + activo);
    });
}
window.addEventListener('scroll', actualizarActivo);
actualizarActivo();
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
        secciones_html = []
        nav_items = []

        for i, sec in enumerate(doc.secciones, 1):
            titulo = sec.titulo or f"Sección {i}"
            sid = f"sec-{i}"
            nav_items.append(f'<a href="#{sid}">{i}. {self._esc(titulo)}</a>')
            parrafos = "".join(
                f"<p>{self._enriquecer(p.strip())}</p>"
                for p in sec.texto.split("\n\n") if p.strip()
            )
            secciones_html.append(
                f'<section class="seccion" id="{sid}">'
                f'<h2>{self._esc(titulo)}</h2>'
                f'{parrafos}'
                f'</section>'
            )

        nav_html = "\n".join(nav_items)
        body_html = "\n".join(secciones_html)
        titulo_esc = self._esc(doc.titulo)

        return f"""<!DOCTYPE html>
<html lang="es">
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
  <h2>&#9776; Contenido</h2>
  <nav>
    <a href="#portada">Inicio</a>
    {nav_html}
  </nav>
</div>
<div id="main">
  <div id="portada">
    <h1>{titulo_esc}</h1>
    <p>{len(doc.secciones)} secciones</p>
  </div>
  {body_html}
</div>
<script>{_JS}</script>
</body>
</html>"""

    def _esc(self, texto: str) -> str:
        return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _enriquecer(self, texto: str) -> str:
        texto = self._esc(texto)
        texto = re.sub(r"\b([A-Z]{2,})\b", r'<span class="tag-sigla">\1</span>', texto)
        texto = re.sub(r"\b(\d+[\.,]?\d*\s*%)", r'<span class="tag-num">\1</span>', texto)
        return texto
