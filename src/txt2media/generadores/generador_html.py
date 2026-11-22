"""Generador HTML: documento de lectura con menú lateral, portada y tres modos claros de lectura.

Un solo archivo autocontenido (CSS y JS en línea). Las fuentes se cargan de
Google Fonts y, sin conexión, se usan las del sistema.
"""

from __future__ import annotations

import base64
import html
import os
import re
import tempfile
from datetime import date
from pathlib import Path

from txt2media.core.modelo import Bloque, Documento, TipoBloque
from txt2media.generadores.estilo import (
    PALETA, _RE_PORCENTAJE, _RE_SIGLA, color_capitulo, formato_miles, minutos_lectura,
    nivel_relativo, numeracion, palabras_de,
)

_P = PALETA

_CSS = f"""
:root {{
  --tinta: {_P.tinta}; --tinta-2: {_P.tinta_2}; --tinta-3: {_P.tinta_3};
  --fondo: {_P.fondo}; --papel: {_P.papel}; --linea: {_P.linea};
  --acento: {_P.acento}; --acento-2: {_P.acento_2}; --acento-suave: {_P.acento_suave};
  --codigo: #F4F6FA; --codigo-txt: #1E293B;
  --hero-a: #EEF4FF; --hero-b: #F4F1FF; --hero-brillo: #E4DEFF;
  --tam: 18px; --ancho: 720px; --f-lectura: var(--f-texto);
  --sombra: 0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.06);
  --f-titulo: 'Figtree', 'Segoe UI', system-ui, sans-serif;
  --f-texto: 'Source Serif 4', 'Georgia', 'Cambria', serif;
  --f-mono: 'JetBrains Mono', 'Cascadia Mono', Consolas, monospace;
  --ancho-menu: 300px;
  color-scheme: light;
}}
/* Tres modos claros de lectura (Blanco es el predeterminado) */
:root[data-tema="sepia"] {{
  --tinta: #3A2E22; --tinta-2: #5C4B39; --tinta-3: #8A7760;
  --fondo: #FAF3E5; --papel: #F3E8D2; --linea: #E4D5B9;
  --acento: #9C5A1F; --acento-2: #B4532A; --acento-suave: #F0E0C4;
  --codigo: #F2E7D1; --codigo-txt: #3A2E22;
  --hero-a: #F6EBD6; --hero-b: #F3E3CB; --hero-brillo: #EBD3AE;
  --sombra: 0 1px 2px rgba(90,60,20,.06), 0 8px 24px rgba(90,60,20,.08);
}}
:root[data-tema="gris"] {{
  --tinta: #262B32; --tinta-2: #4B525C; --tinta-3: #7C848F;
  --fondo: #EEF0F2; --papel: #E5E8EC; --linea: #D5DAE0;
  --acento: #3A5D8F; --acento-2: #5A5EA6; --acento-suave: #DDE4EE;
  --codigo: #E3E6EA; --codigo-txt: #262B32;
  --hero-a: #E6EAF0; --hero-b: #EAEAF1; --hero-brillo: #D6DDE8;
}}
*, *::before, *::after {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }}
body {{ margin: 0; background: var(--fondo); color: var(--tinta);
  font: var(--tam)/1.75 var(--f-lectura); transition: background .3s, color .3s; text-rendering: optimizeLegibility; }}
a {{ color: var(--acento); }}
::selection {{ background: var(--acento-suave); }}

/* Barra de progreso */
#progreso {{ position: fixed; top: 0; left: 0; height: 3px; width: 0;
  background: linear-gradient(90deg, var(--acento), var(--acento-2)); z-index: 50; transition: width .1s linear; }}

/* Menú lateral */
#menu {{ position: fixed; inset: 0 auto 0 0; width: var(--ancho-menu); background: var(--papel);
  border-right: 1px solid var(--linea); display: flex; flex-direction: column; z-index: 40;
  font-family: var(--f-titulo); transition: transform .25s ease; }}
.menu-cab {{ padding: 24px 22px 16px; border-bottom: 1px solid var(--linea); }}
.marca {{ display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 700;
  letter-spacing: .12em; text-transform: uppercase; color: var(--tinta-3); }}
.marca i {{ width: 8px; height: 8px; border-radius: 2px; background: linear-gradient(135deg, var(--acento), var(--acento-2)); }}
.menu-titulo {{ margin: 10px 0 0; font-size: 16px; line-height: 1.35; font-weight: 700; color: var(--tinta); }}
.buscar {{ margin: 14px 0 0; width: 100%; padding: 9px 12px; border: 1px solid var(--linea); border-radius: 8px;
  background: var(--fondo); color: var(--tinta); font: 14px var(--f-titulo); }}
.buscar:focus {{ outline: 2px solid var(--acento); outline-offset: -1px; }}
#indice {{ flex: 1; overflow-y: auto; padding: 10px 10px 24px; }}
#indice a {{ display: flex; gap: 10px; align-items: baseline; padding: 7px 12px; border-radius: 8px;
  color: var(--tinta-2); text-decoration: none; font-size: 14px; line-height: 1.4; border-left: 3px solid transparent; }}
#indice a:hover {{ background: var(--fondo); color: var(--tinta); }}
#indice a.activo {{ background: var(--fondo); color: var(--tinta); border-left-color: var(--c); box-shadow: var(--sombra); font-weight: 600; }}
#indice a .n {{ font: 600 11px/1.8 var(--f-mono); color: var(--c); min-width: 2.4em; }}
#indice a.n2 {{ padding-left: 26px; font-size: 13px; }}
#indice a.n3 {{ padding-left: 40px; font-size: 13px; }}
#indice a.oculto {{ display: none; }}
.menu-pie {{ padding: 12px 22px; border-top: 1px solid var(--linea); display: flex; justify-content: space-between;
  align-items: center; font-size: 12px; color: var(--tinta-3); }}
.boton {{ border: 1px solid var(--linea); background: var(--fondo); color: var(--tinta-2); border-radius: 8px;
  padding: 6px 10px; font: 600 12px var(--f-titulo); cursor: pointer; }}
.boton:hover {{ color: var(--tinta); border-color: var(--tinta-3); }}
.lectura {{ padding: 14px 22px; border-top: 1px solid var(--linea); display: grid; gap: 10px; }}
.lectura .rot {{ font: 700 10px var(--f-titulo); letter-spacing: .14em; text-transform: uppercase; color: var(--tinta-3); }}
.modos {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
.modos button {{ border: 1px solid var(--linea); border-radius: 8px; padding: 8px 4px; cursor: pointer;
  font: 600 12px var(--f-titulo); background: var(--m-fondo); color: var(--m-tinta); }}
.modos button[aria-pressed="true"] {{ outline: 2px solid var(--acento); outline-offset: 1px; }}
.letra {{ display: flex; align-items: center; gap: 6px; }}
.letra .boton {{ flex: 1; }}
.seg {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
.seg.dos {{ grid-template-columns: repeat(2, 1fr); }}
.seg button {{ border: 1px solid var(--linea); border-radius: 8px; padding: 7px 4px; cursor: pointer; background: var(--fondo);
  color: var(--tinta-2); font: 600 12px var(--f-titulo); }}
.seg button[aria-pressed="true"] {{ color: var(--acento); border-color: var(--acento); background: var(--acento-suave); }}
#avance {{ position: fixed; left: calc(var(--ancho-menu) + 20px); bottom: 20px; z-index: 30; padding: 7px 12px;
  border-radius: 999px; background: color-mix(in srgb, var(--fondo) 92%, transparent); border: 1px solid var(--linea);
  box-shadow: var(--sombra); font: 600 12px var(--f-titulo); color: var(--tinta-2); backdrop-filter: blur(6px); }}
#aviso {{ position: fixed; left: 50%; top: 20px; transform: translate(-50%, -20px); opacity: 0; z-index: 60;
  padding: 10px 16px; border-radius: 10px; background: var(--tinta); color: var(--fondo); font: 600 13px var(--f-titulo);
  transition: opacity .3s, transform .3s; pointer-events: none; }}
#aviso.ver {{ opacity: 1; transform: translate(-50%, 0); }}
.letra span {{ font: 600 12px var(--f-mono); color: var(--tinta-3); min-width: 42px; text-align: center; }}

/* Contenido */
main {{ margin-left: var(--ancho-menu); }}
.portada {{ position: relative; overflow: hidden; padding: 96px 8vw 72px; color: var(--tinta);
  background: radial-gradient(900px 420px at 90% -20%, var(--hero-brillo) 0%, transparent 60%),
              linear-gradient(135deg, var(--hero-a) 0%, var(--hero-b) 100%);
  border-bottom: 1px solid var(--linea); }}
.portada::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
  background: linear-gradient(180deg, var(--acento), var(--acento-2)); }}
.portada::after {{ content: ""; position: absolute; inset: auto -10% -60% auto; width: 520px; height: 520px;
  border: 1px solid color-mix(in srgb, var(--acento) 22%, transparent); border-radius: 50%; }}
.portada .etiqueta {{ font: 700 12px var(--f-titulo); letter-spacing: .16em; text-transform: uppercase; color: var(--acento); }}
.portada h1 {{ font: 800 clamp(34px, 5vw, 60px)/1.05 var(--f-titulo); letter-spacing: -.02em; margin: 14px 0 12px; max-width: 18ch; text-wrap: balance; }}
.portada .autor {{ font: 500 20px var(--f-titulo); color: var(--tinta-2); }}
.datos {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 34px; }}
.dato {{ background: color-mix(in srgb, var(--fondo) 85%, transparent); border: 1px solid var(--linea); box-shadow: var(--sombra);
  border-radius: 12px; padding: 10px 16px; font-family: var(--f-titulo); }}
.dato b {{ display: block; font-size: 20px; line-height: 1.1; color: var(--acento); }}
.dato span {{ font-size: 12px; color: var(--tinta-3); letter-spacing: .04em; }}

.cuerpo {{ max-width: calc(var(--ancho) + 64px); margin: 0 auto; padding: 56px 32px 120px; }}
.seccion {{ padding-top: 40px; scroll-margin-top: 24px; }}
.seccion + .seccion {{ border-top: 1px solid var(--linea); margin-top: 40px; }}
.sec-cab {{ display: flex; gap: 16px; align-items: flex-start; margin-bottom: 22px; }}
.sec-num {{ flex: none; min-width: 44px; height: 44px; padding: 0 8px; border-radius: 12px; display: grid; place-items: center;
  background: color-mix(in srgb, var(--c) 12%, transparent); color: var(--c); font: 700 15px var(--f-mono); }}
.seccion h2 {{ margin: 4px 0 0; font: 700 30px/1.2 var(--f-titulo); letter-spacing: -.01em; text-wrap: balance; }}
.seccion.n2 h2 {{ font-size: 24px; }}
.seccion.n3 h2 {{ font-size: 20px; }}
.seccion p {{ margin: 0 0 1.1em; hyphens: auto; }}
.seccion p.capitular::first-letter {{ float: left; font: 700 3.4em/0.85 var(--f-titulo);
  margin: .08em .1em 0 0; color: var(--c); }}
.seccion ul {{ margin: 0 0 1.2em; padding-left: 0; list-style: none; }}
.seccion li {{ position: relative; padding-left: 26px; margin-bottom: .45em; }}
.seccion li::before {{ content: ""; position: absolute; left: 6px; top: .72em; width: 7px; height: 7px; border-radius: 2px; background: var(--c); }}
blockquote {{ margin: 1.6em 0; padding: 18px 24px; border-left: 4px solid var(--c); background: var(--papel);
  border-radius: 0 12px 12px 0; font-style: italic; color: var(--tinta-2); font-size: 1.05em; }}
pre, .tabla, blockquote, figure, ul, .notas {{ clear: both; }}
.bloques::after {{ content: ""; display: block; clear: both; }}
pre {{ position: relative; border: 1px solid var(--linea); margin: 1.5em 0; padding: 18px 20px; background: var(--codigo); color: var(--codigo-txt);
  border-radius: 12px; overflow-x: auto; font: 14px/1.6 var(--f-mono); }}
pre .copiar {{ position: absolute; top: 10px; right: 10px; }}
pre .lang {{ position: absolute; top: 12px; right: 84px; font: 600 11px var(--f-titulo); letter-spacing: .08em; text-transform: uppercase; color: var(--tinta-3); }}
.tabla {{ margin: 1.6em 0; overflow-x: auto; border: 1px solid var(--linea); border-radius: 12px; box-shadow: var(--sombra); }}
table {{ border-collapse: collapse; width: 100%; font: 15px/1.5 var(--f-titulo); }}
thead th {{ position: sticky; top: 0; background: color-mix(in srgb, var(--c) 13%, var(--fondo)); color: color-mix(in srgb, var(--c) 80%, var(--tinta));
  text-align: left; padding: 11px 14px; font-weight: 700; border-bottom: 2px solid color-mix(in srgb, var(--c) 45%, transparent); }}
td {{ padding: 10px 14px; border-top: 1px solid var(--linea); vertical-align: top; }}
tbody tr:nth-child(even) td {{ background: var(--papel); }}
tbody tr:hover td {{ background: var(--acento-suave); }}
figure {{ margin: 1.8em 0; }}
figure img {{ max-width: 100%; height: auto; border-radius: 12px; box-shadow: var(--sombra); }}
.caption, figcaption {{ font: 14px/1.5 var(--f-titulo); color: var(--tinta-3); margin: -.4em 0 1.4em; }}
hr.sep {{ border: 0; height: 1px; margin: 2.4em auto; width: 40%; background: linear-gradient(90deg, transparent, var(--linea), transparent); }}
.notas {{ margin-top: 1.8em; padding: 16px 20px; border: 1px dashed var(--linea); border-radius: 12px;
  font: 14px/1.55 var(--f-titulo); color: var(--tinta-2); }}
.notas b {{ display: block; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--tinta-3); margin-bottom: 6px; }}
.notas p {{ margin: 0 0 .4em; }}
abbr.sigla {{ text-decoration: none; font-size: .88em; letter-spacing: .06em; }}
mark.pct {{ background: none; color: var(--c); font-weight: 700; font-family: var(--f-titulo); }}
.fin {{ margin-top: 80px; padding-top: 24px; border-top: 1px solid var(--linea); font: 13px var(--f-titulo);
  color: var(--tinta-3); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }}

#arriba {{ position: fixed; right: 24px; bottom: 24px; width: 44px; height: 44px; border-radius: 50%;
  border: 1px solid var(--linea); background: var(--fondo); color: var(--tinta-2); box-shadow: var(--sombra);
  font: 700 18px var(--f-titulo); cursor: pointer; opacity: 0; pointer-events: none; transition: opacity .2s; z-index: 30; }}
#arriba.ver {{ opacity: 1; pointer-events: auto; }}
#abrir-menu {{ display: none; position: fixed; top: 14px; left: 14px; z-index: 45; }}

@media (max-width: 960px) {{
  #menu {{ transform: translateX(-100%); box-shadow: var(--sombra); }}
  body.menu-abierto #menu {{ transform: none; }}
  main {{ margin-left: 0; }}
  #abrir-menu {{ display: block; }}
  #avance {{ left: 14px; bottom: 14px; }}
  .portada {{ padding: 88px 24px 56px; }}
  .cuerpo {{ padding: 40px 20px 100px; }}
  body {{ font-size: 17px; }}
}}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} * {{ transition: none !important; }} }}
@media print {{
  #menu, #progreso, #arriba, #abrir-menu, #avance, #aviso, pre .copiar {{ display: none !important; }}
  main {{ margin: 0; }}
  .portada {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; padding: 60px 40px; page-break-after: always; }}
  .seccion {{ page-break-inside: avoid; }}
  body {{ font-size: 12pt; }}
}}
"""

_JS = r"""
(function () {
  var raiz = document.documentElement;
  function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function leer(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } }

  var modos = document.querySelectorAll('.modos button');
  function modo(m) {
    if (m === 'blanco') delete raiz.dataset.tema; else raiz.dataset.tema = m;
    modos.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.tema === m)); });
  }
  modo(leer('txt2media-modo', 'blanco'));
  modos.forEach(function (b) { b.addEventListener('click', function () { modo(b.dataset.tema); guardar('txt2media-modo', b.dataset.tema); }); });

  var escala = parseInt(leer('txt2media-letra', '100'), 10) || 100;
  function letra(v) {
    escala = Math.max(80, Math.min(140, v));
    raiz.style.setProperty('--tam', (18 * escala / 100).toFixed(1) + 'px');
    document.getElementById('tam').textContent = escala + '%';
    guardar('txt2media-letra', String(escala));
  }
  letra(escala);
  document.getElementById('menos').addEventListener('click', function () { letra(escala - 10); });
  document.getElementById('mas').addEventListener('click', function () { letra(escala + 10); });

  function grupo(id, clave, defecto, aplicarValor) {
    var botones = document.querySelectorAll('#' + id + ' button');
    function poner(v) {
      aplicarValor(v);
      botones.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.v === v)); });
      guardar(clave, v);
    }
    poner(leer(clave, defecto));
    botones.forEach(function (b) { b.addEventListener('click', function () { poner(b.dataset.v); }); });
  }
  grupo('fuentes', 'txt2media-fuente', 'serif', function (v) {
    raiz.style.setProperty('--f-lectura', v === 'sans' ? 'var(--f-titulo)' : 'var(--f-texto)');
  });
  grupo('anchos', 'txt2media-ancho', '720', function (v) { raiz.style.setProperty('--ancho', v + 'px'); });

  var enlaces = Array.prototype.slice.call(document.querySelectorAll('#indice a'));
  var porId = {};
  enlaces.forEach(function (a) { porId[a.getAttribute('href').slice(1)] = a; });
  var actual = null;
  var obs = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (e.isIntersecting) {
        if (actual) actual.classList.remove('activo');
        actual = porId[e.target.id];
        if (actual) { actual.classList.add('activo'); actual.scrollIntoView({ block: 'nearest' }); }
      }
    });
  }, { rootMargin: '-15% 0px -75% 0px' });
  document.querySelectorAll('.seccion').forEach(function (s) { obs.observe(s); });

  var barra = document.getElementById('progreso'), arriba = document.getElementById('arriba');
  var avance = document.getElementById('avance'), minutos = MINUTOS;
  var claveLectura = 'txt2media-pos-' + document.title;
  var pendiente = null;
  function alDesplazar() {
    var h = document.documentElement;
    var p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight);
    barra.style.width = (p * 100).toFixed(2) + '%';
    arriba.classList.toggle('ver', h.scrollTop > 600);
    var resta = Math.max(0, Math.ceil(minutos * (1 - p)));
    avance.textContent = Math.round(p * 100) + ' % leído · ' + (resta ? resta + ' min restantes' : 'terminado');
    clearTimeout(pendiente);
    pendiente = setTimeout(function () { guardar(claveLectura, String(p)); }, 400);
  }
  window.addEventListener('scroll', alDesplazar, { passive: true });
  // Retomar donde se dejó la lectura
  var previa = parseFloat(leer(claveLectura, '0'));
  if (previa > 0.02 && previa < 0.98 && !location.hash) {
    var h = document.documentElement;
    window.scrollTo(0, previa * (h.scrollHeight - h.clientHeight));
    var aviso = document.getElementById('aviso');
    aviso.textContent = 'Continúas donde lo dejaste (' + Math.round(previa * 100) + ' %)';
    aviso.classList.add('ver');
    setTimeout(function () { aviso.classList.remove('ver'); }, 3200);
  }
  alDesplazar();
  arriba.addEventListener('click', function () { window.scrollTo({ top: 0 }); });

  document.getElementById('buscar').addEventListener('input', function () {
    var q = this.value.trim().toLowerCase();
    enlaces.forEach(function (a) { a.classList.toggle('oculto', q && a.textContent.toLowerCase().indexOf(q) < 0); });
  });

  document.getElementById('abrir-menu').addEventListener('click', function () { document.body.classList.toggle('menu-abierto'); });
  enlaces.forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('menu-abierto'); }); });

  document.querySelectorAll('pre .copiar').forEach(function (b) {
    b.addEventListener('click', function () {
      var codigo = b.parentNode.querySelector('code').innerText;
      var fin = function () { b.textContent = 'Copiado'; setTimeout(function () { b.textContent = 'Copiar'; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(codigo).then(fin, fin); else fin();
    });
  });
})();
"""


_RE_NUM_TITULO = re.compile(r"^\s*(\d+(?:\.\d+)*)[.)]?\s+(\S.*)$")


def _esc(t: str) -> str:
    return html.escape(t or "", quote=True)


def _enriquecer(texto: str) -> str:
    t = _esc(texto.strip())
    t = _RE_PORCENTAJE.sub(r'<mark class="pct">\1</mark>', t)
    t = _RE_SIGLA.sub(r'<abbr class="sigla">\1</abbr>', t)
    return t


class GeneradorHTML:
    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        contenido = self._construir(doc)
        fd, tmp = tempfile.mkstemp(suffix=".html", dir=salida.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(contenido)
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return salida

    # ------------------------------------------------------------------ #
    def _construir(self, doc: Documento) -> str:
        secciones = doc.secciones
        numeros = numeracion(secciones)
        palabras = palabras_de(doc)
        titulo = doc.titulo or "Documento"

        indice, cuerpo = [], []
        for i, sec in enumerate(secciones):
            nivel = nivel_relativo(secciones, sec)
            color = color_capitulo(i)
            sid = f"s{i + 1}"
            nombre = sec.titulo or f"Sección {numeros[i]}"
            m = _RE_NUM_TITULO.match(nombre)
            if m:  # el título ya trae su número: se usa ese y no se repite
                numeros[i], nombre = m.group(1), m.group(2)
            clase = f"n{min(nivel, 3)}"
            indice.append(
                f'<a href="#{sid}" class="{clase}" style="--c:{color}">'
                f'<span class="n">{numeros[i]}</span><span>{_esc(nombre)}</span></a>'
            )
            cuerpo.append(
                f'<section class="seccion {clase}" id="{sid}" style="--c:{color}">'
                f'<header class="sec-cab"><span class="sec-num">{numeros[i]}</span>'
                f'<h2>{_esc(nombre)}</h2></header>'
                f'<div class="bloques">{self._bloques(sec.bloques, capitular=nivel == 1)}</div></section>'
            )

        datos = [
            (str(len(secciones)), "secciones"),
            (formato_miles(palabras), "palabras"),
            (f"{minutos_lectura(palabras)} min", "de lectura"),
        ]
        if doc.ruta_origen:
            datos.append((Path(doc.ruta_origen).suffix.lstrip(".").upper() or "—", "origen"))
        datos_html = "".join(f'<div class="dato"><b>{_esc(v)}</b><span>{_esc(k)}</span></div>' for v, k in datos)
        autor = f'<div class="autor">{_esc(doc.autor)}</div>' if doc.autor else ""
        hoy = date.today().strftime("%d/%m/%Y")

        return f"""<!DOCTYPE html>
<html lang="{_esc(doc.idioma or 'es')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="txt2media">
<title>{_esc(titulo)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>{_CSS}</style>
</head>
<body>
<div id="progreso" aria-hidden="true"></div>
<button id="abrir-menu" class="boton" aria-label="Abrir índice">☰ Índice</button>
<aside id="menu" aria-label="Índice del documento">
  <div class="menu-cab">
    <div class="marca"><i></i>txt2media</div>
    <p class="menu-titulo">{_esc(titulo)}</p>
    <input id="buscar" class="buscar" type="search" placeholder="Buscar sección…" aria-label="Buscar sección">
  </div>
  <nav id="indice">{''.join(indice)}</nav>
  <div class="lectura">
    <span class="rot">Modo de lectura</span>
    <div class="modos" role="group" aria-label="Modo de lectura">
      <button type="button" data-tema="blanco" style="--m-fondo:#FFFFFF;--m-tinta:#12171D">Blanco</button>
      <button type="button" data-tema="sepia" style="--m-fondo:#FAF3E5;--m-tinta:#3A2E22">Sepia</button>
      <button type="button" data-tema="gris" style="--m-fondo:#EEF0F2;--m-tinta:#262B32">Gris suave</button>
    </div>
    <span class="rot">Tipografía</span>
    <div class="seg dos" id="fuentes" role="group" aria-label="Tipografía">
      <button type="button" data-v="serif" style="font-family:var(--f-texto)">Serifa</button>
      <button type="button" data-v="sans" style="font-family:var(--f-titulo)">Sin serifa</button>
    </div>
    <span class="rot">Ancho de línea</span>
    <div class="seg" id="anchos" role="group" aria-label="Ancho de línea">
      <button type="button" data-v="600">Estrecho</button>
      <button type="button" data-v="720">Normal</button>
      <button type="button" data-v="880">Ancho</button>
    </div>
    <span class="rot">Tamaño de letra</span>
    <div class="letra" role="group" aria-label="Tamaño de letra">
      <button type="button" class="boton" id="menos" aria-label="Letra más pequeña">A−</button>
      <span id="tam">100%</span>
      <button type="button" class="boton" id="mas" aria-label="Letra más grande">A+</button>
    </div>
  </div>
  <div class="menu-pie"><span>{len(secciones)} secciones</span><span>{minutos_lectura(palabras)} min de lectura</span></div>
</aside>
<main>
  <header class="portada" id="inicio">
    <div class="etiqueta">Documento</div>
    <h1>{_esc(titulo)}</h1>
    {autor}
    <div class="datos">{datos_html}</div>
  </header>
  <div class="cuerpo">
    {''.join(cuerpo)}
    <footer class="fin"><span>{_esc(titulo)}</span><span>Generado con txt2media · {hoy}</span></footer>
  </div>
</main>
<button id="arriba" type="button" aria-label="Volver arriba">↑</button>
<div id="avance" aria-live="off">0 % leído</div>
<div id="aviso" role="status"></div>
<script>{_JS.replace('MINUTOS', str(minutos_lectura(palabras)))}</script>
</body>
</html>"""

    # ------------------------------------------------------------------ #
    def _bloques(self, bloques: list[Bloque], capitular: bool = False) -> str:
        partes: list[str] = []
        notas: list[str] = []
        primero = True
        for b in bloques:
            t = b.tipo
            if t == TipoBloque.PARRAFO and b.contenido.strip():
                texto = _enriquecer(b.contenido)
                if b.negrita:
                    texto = f"<strong>{texto}</strong>"
                if b.cursiva:
                    texto = f"<em>{texto}</em>"
                # Letra capital solo en el primer párrafo largo de un capítulo
                clase = ' class="capitular"' if capitular and primero and len(b.contenido) > 160 else ""
                partes.append(f"<p{clase}>{texto}</p>")
                primero = False
            elif t == TipoBloque.TITULO and b.contenido.strip():
                partes.append(f'<h3 style="font:700 21px/1.3 var(--f-titulo);margin:1.6em 0 .6em">{_esc(b.contenido)}</h3>')
            elif t == TipoBloque.LISTA and b.items_lista:
                items = "".join(f"<li>{_enriquecer(it)}</li>" for it in b.items_lista)
                partes.append(f"<ul>{items}</ul>")
            elif t == TipoBloque.CITA and b.contenido.strip():
                partes.append(f"<blockquote>{_enriquecer(b.contenido)}</blockquote>")
            elif t == TipoBloque.CODIGO and b.contenido:
                lang = f'<span class="lang">{_esc(b.idioma_codigo)}</span>' if b.idioma_codigo else ""
                partes.append(
                    f'<pre>{lang}<button class="boton copiar" type="button">Copiar</button>'
                    f"<code>{_esc(b.contenido)}</code></pre>"
                )
            elif t == TipoBloque.TABLA and b.tabla:
                partes.append(self._tabla(b))
            elif t == TipoBloque.IMAGEN and b.imagen:
                partes.append(self._imagen(b))
            elif t == TipoBloque.CAPTION and b.contenido.strip():
                partes.append(f'<p class="caption">{_esc(b.contenido)}</p>')
            elif t == TipoBloque.NOTA_PIE and b.contenido.strip():
                notas.append(f"<p>{_esc(b.contenido)}</p>")
            elif t == TipoBloque.SEPARADOR:
                partes.append('<hr class="sep">')
        if notas:
            partes.append(f'<aside class="notas"><b>Notas</b>{"".join(notas)}</aside>')
        return "".join(partes)

    def _tabla(self, b: Bloque) -> str:
        t = b.tabla
        filas = list(t.filas)
        encabezados = list(t.encabezados)
        if not encabezados:
            cab = [f for f in filas if f.es_encabezado]
            if cab:
                encabezados = cab[0].celdas
                filas = [f for f in filas if f is not cab[0]]
        thead = ""
        if encabezados:
            thead = "<thead><tr>" + "".join(f"<th>{_esc(c)}</th>" for c in encabezados) + "</tr></thead>"
        tbody = "".join(
            "<tr>" + "".join(f"<td>{_enriquecer(c)}</td>" for c in f.celdas) + "</tr>" for f in filas
        )
        return f'<div class="tabla"><table>{thead}<tbody>{tbody}</tbody></table></div>'

    def _imagen(self, b: Bloque) -> str:
        img = b.imagen
        datos = img.datos
        if datos is None and img.ruta and Path(img.ruta).exists():
            try:
                datos = Path(img.ruta).read_bytes()
            except OSError:
                datos = None
        if not datos:
            return ""
        tipo = "image/png"
        if datos[:3] == b"\xff\xd8\xff":
            tipo = "image/jpeg"
        elif datos[:4] == b"GIF8":
            tipo = "image/gif"
        elif datos[:4] == b"RIFF":
            tipo = "image/webp"
        src = f"data:{tipo};base64,{base64.b64encode(datos).decode('ascii')}"
        alt = _esc(img.alt)
        pie = f"<figcaption>{alt}</figcaption>" if img.alt else ""
        return f'<figure><img src="{src}" alt="{alt}" loading="lazy">{pie}</figure>'
