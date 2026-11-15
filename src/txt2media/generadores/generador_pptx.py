"""Generador PPTX usando python-pptx."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from txt2media.core.modelo import Documento, TipoBloque
from txt2media.core.tema import TEMA


_EMU_POR_CM = 360000
_ANCHO_SLIDE = 24 * _EMU_POR_CM
_ALTO_SLIDE = 13.5 * _EMU_POR_CM


class GeneradorPPTX:
    def generar(self, doc: Documento, salida: Path, opciones: dict) -> None:
        from pptx import Presentation
        from pptx.util import Emu, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = Presentation()
        prs.slide_width = Emu(_ANCHO_SLIDE)
        prs.slide_height = Emu(_ALTO_SLIDE)

        self._agregar_portada(prs, doc.titulo)

        for sec in doc.secciones:
            if not sec.bloques and not sec.titulo:
                continue
            self._agregar_seccion(prs, sec)

        salida.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".pptx", dir=salida.parent)
        os.close(fd)
        try:
            prs.save(tmp)
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def _agregar_portada(self, prs, titulo: str) -> None:
        from pptx.util import Emu, Pt
        from pptx.dml.color import RGBColor

        layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(layout)

        fondo = slide.shapes.add_shape(
            1,
            Emu(0), Emu(0),
            Emu(_ANCHO_SLIDE), Emu(_ALTO_SLIDE),
        )
        fondo.fill.solid()
        fondo.fill.fore_color.rgb = RGBColor.from_string(TEMA.azul.lstrip("#"))
        fondo.line.fill.background()

        barra = slide.shapes.add_shape(
            1,
            Emu(0), Emu(_ALTO_SLIDE - 1 * _EMU_POR_CM),
            Emu(_ANCHO_SLIDE), Emu(1 * _EMU_POR_CM),
        )
        barra.fill.solid()
        barra.fill.fore_color.rgb = RGBColor.from_string(TEMA.naranja.lstrip("#"))
        barra.line.fill.background()

        txb = slide.shapes.add_textbox(
            Emu(2 * _EMU_POR_CM),
            Emu(4 * _EMU_POR_CM),
            Emu(20 * _EMU_POR_CM),
            Emu(4 * _EMU_POR_CM),
        )
        tf = txb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = titulo[:80]
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    def _agregar_seccion(self, prs, sec) -> None:
        from pptx.util import Emu, Pt
        from pptx.dml.color import RGBColor

        layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(layout)

        encabezado = slide.shapes.add_shape(
            1,
            Emu(0), Emu(0),
            Emu(_ANCHO_SLIDE), Emu(2 * _EMU_POR_CM),
        )
        encabezado.fill.solid()
        encabezado.fill.fore_color.rgb = RGBColor.from_string(TEMA.azul.lstrip("#"))
        encabezado.line.fill.background()

        if sec.titulo:
            txb_titulo = slide.shapes.add_textbox(
                Emu(0.5 * _EMU_POR_CM),
                Emu(0.3 * _EMU_POR_CM),
                Emu(23 * _EMU_POR_CM),
                Emu(1.5 * _EMU_POR_CM),
            )
            tf = txb_titulo.text_frame
            p = tf.paragraphs[0]
            p.text = sec.titulo[:80]
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        y_actual = 2.3 * _EMU_POR_CM
        for bloque in sec.bloques[:6]:
            if y_actual > _ALTO_SLIDE - _EMU_POR_CM:
                break
            if bloque.tipo == TipoBloque.PARRAFO and bloque.contenido:
                txb = slide.shapes.add_textbox(
                    Emu(0.8 * _EMU_POR_CM),
                    Emu(y_actual),
                    Emu(22.5 * _EMU_POR_CM),
                    Emu(1.8 * _EMU_POR_CM),
                )
                tf = txb.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = bloque.contenido[:200]
                p.font.size = Pt(16)
                p.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
                y_actual += 2 * _EMU_POR_CM

            elif bloque.tipo == TipoBloque.LISTA and bloque.items_lista:
                for item in bloque.items_lista[:5]:
                    if y_actual > _ALTO_SLIDE - _EMU_POR_CM:
                        break
                    txb = slide.shapes.add_textbox(
                        Emu(1.2 * _EMU_POR_CM),
                        Emu(y_actual),
                        Emu(22 * _EMU_POR_CM),
                        Emu(0.9 * _EMU_POR_CM),
                    )
                    tf = txb.text_frame
                    p = tf.paragraphs[0]
                    p.text = f"• {item[:120]}"
                    p.font.size = Pt(15)
                    p.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
                    y_actual += 1.1 * _EMU_POR_CM

        barra_inf = slide.shapes.add_shape(
            1,
            Emu(0), Emu(_ALTO_SLIDE - 0.3 * _EMU_POR_CM),
            Emu(_ANCHO_SLIDE), Emu(0.3 * _EMU_POR_CM),
        )
        barra_inf.fill.solid()
        barra_inf.fill.fore_color.rgb = RGBColor.from_string(TEMA.naranja.lstrip("#"))
        barra_inf.line.fill.background()
