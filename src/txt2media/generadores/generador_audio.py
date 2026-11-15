"""Generador de audio TTS — completo o por capítulos (v1.0.1)."""

from __future__ import annotations

import logging
import os
import re
import tempfile
import unicodedata
from pathlib import Path

from txt2media.core.modelo import Documento, Seccion, TipoBloque

_log = logging.getLogger("txt2media.generador_audio")
_VOZ_DEFAULT = "es-PE-CamilaNeural"


class GeneradorAudio:
    def __init__(self, voz: str = _VOZ_DEFAULT) -> None:
        from txt2media.motores.cadena_voz import CadenaVoz

        self._cadena = CadenaVoz(voz=voz)

    # ------------------------------------------------------------------ #
    # Modo completo: un solo MP3 con todo el texto                        #
    # ------------------------------------------------------------------ #
    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        texto = _documento_a_texto(doc)
        if not texto.strip():
            raise ValueError("El documento no contiene texto sintetizable")
        salida.parent.mkdir(parents=True, exist_ok=True)
        self._cadena.sintetizar(texto, salida)
        return salida

    # ------------------------------------------------------------------ #
    # Modo capítulos: un MP3 por sección + cover.jpg + playlist.m3u      #
    # ------------------------------------------------------------------ #
    def generar_capitulos(self, doc: Documento, carpeta_salida: Path) -> list[Path]:
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        archivos: list[Path] = []
        titulos: list[str] = []

        for idx, sec in enumerate(doc.secciones, start=1):
            texto = _texto_de_seccion(sec)
            if not texto.strip():
                continue
            nombre = _nombre_capitulo(idx, sec.titulo or f"capitulo_{idx}")
            salida = carpeta_salida / nombre
            try:
                self._cadena.sintetizar(texto, salida)
                archivos.append(salida)
                titulos.append(sec.titulo or f"Capítulo {idx}")
                _log.info("Capítulo %d generado: %s", idx, nombre)
            except Exception as exc:
                _log.warning("Capítulo %d omitido (%s): %s", idx, nombre, exc)

        if archivos:
            _generar_cover(doc.titulo, carpeta_salida)
            _generar_playlist(archivos, carpeta_salida, titulos)

        return archivos


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _documento_a_texto(doc: Documento) -> str:
    partes: list[str] = [doc.titulo]
    for sec in doc.secciones:
        partes.append(_texto_de_seccion(sec))
    return "\n\n".join(p for p in partes if p.strip())


def _texto_de_seccion(sec: Seccion) -> str:
    partes: list[str] = []
    if sec.titulo:
        partes.append(sec.titulo)
    for bloque in sec.bloques:
        if bloque.tipo == TipoBloque.PARRAFO and bloque.contenido:
            partes.append(bloque.contenido)
        elif bloque.tipo == TipoBloque.LISTA and bloque.items_lista:
            partes.extend(bloque.items_lista)
        elif bloque.tipo == TipoBloque.CITA and bloque.contenido:
            partes.append(bloque.contenido)
    return "\n".join(partes)


def _nombre_capitulo(idx: int, titulo: str) -> str:
    slug = unicodedata.normalize("NFKD", titulo)
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", slug).strip().lower()
    slug = re.sub(r"[\s_-]+", "_", slug)[:40]
    if not slug:
        slug = f"capitulo_{idx}"
    return f"{idx:02d}_{slug}.mp3"


def _generar_cover(titulo: str, carpeta: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
        from txt2media.core.tema import TEMA

        img = Image.new("RGB", (400, 600), color=TEMA.azul)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (400, 8)], fill=TEMA.naranja)
        draw.rectangle([(0, 592), (400, 600)], fill=TEMA.naranja)

        try:
            fuente = ImageFont.truetype("arial.ttf", 28)
        except Exception:
            fuente = ImageFont.load_default()

        lineas = _partir_texto(titulo, 20)
        y = 240
        for linea in lineas[:4]:
            try:
                bbox = draw.textbbox((0, 0), linea, font=fuente)
                w = bbox[2] - bbox[0]
                x = (400 - w) // 2
            except Exception:
                x = 20
            draw.text((x, y), linea, fill="white", font=fuente)
            y += 40

        ruta_cover = carpeta / "cover.jpg"
        fd, tmp = tempfile.mkstemp(suffix=".jpg", dir=carpeta)
        os.close(fd)
        try:
            img.save(tmp, "JPEG", quality=85)
            os.replace(tmp, ruta_cover)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    except Exception as exc:
        _log.warning("No se pudo generar cover.jpg: %s", exc)


def _partir_texto(texto: str, max_chars: int) -> list[str]:
    palabras = texto.split()
    lineas: list[str] = []
    actual = ""
    for palabra in palabras:
        if len(actual) + len(palabra) + 1 <= max_chars:
            actual = f"{actual} {palabra}".strip()
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def _generar_playlist(archivos: list[Path], carpeta: Path, titulos: list[str]) -> None:
    lineas = ["#EXTM3U"]
    for archivo, titulo in zip(archivos, titulos):
        lineas.append(f"#EXTINF:-1,{titulo}")
        lineas.append(archivo.name)
    contenido = "\n".join(lineas) + "\n"

    ruta_playlist = carpeta / "playlist.m3u"
    fd, tmp = tempfile.mkstemp(suffix=".m3u", dir=carpeta)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(contenido)
        os.replace(tmp, ruta_playlist)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
