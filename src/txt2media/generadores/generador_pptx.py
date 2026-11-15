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
        for bloque in sec.bloques[:8]:
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
                run = p.add_run()
                run.text = bloque.contenido[:200]
                run.font.size = Pt(16)
                run.font.bold = bloque.negrita or None
                run.font.italic = bloque.cursiva or None
                run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
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

            elif bloque.tipo == TipoBloque.CAPTION and bloque.contenido:
                txb = slide.shapes.add_textbox(
                    Emu(0.8 * _EMU_POR_CM),
                    Emu(y_actual),
                    Emu(22.5 * _EMU_POR_CM),
                    Emu(0.7 * _EMU_POR_CM),
                )
                tf = txb.text_frame
                p = tf.paragraphs[0]
                p.text = bloque.contenido[:160]
                p.font.size = Pt(11)
                p.font.italic = True
                p.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
                y_actual += 0.9 * _EMU_POR_CM

            elif bloque.tipo == TipoBloque.TABLA and bloque.tabla:
                t = bloque.tabla
                n_cols = max(len(t.encabezados), max((len(f.celdas) for f in t.filas), default=0))
                n_filas = (1 if t.encabezados else 0) + len(t.filas)
                if n_cols == 0 or n_filas == 0:
                    continue
                alto_tabla = min(n_filas * 0.55 * _EMU_POR_CM, 4 * _EMU_POR_CM)
                ancho_tabla = 22 * _EMU_POR_CM
                if y_actual + alto_tabla > _ALTO_SLIDE - _EMU_POR_CM:
                    break
                tabla_shape = slide.shapes.add_table(
                    n_filas, n_cols,
                    Emu(0.8 * _EMU_POR_CM), Emu(y_actual),
                    Emu(ancho_tabla), Emu(alto_tabla),
                )
                tbl = tabla_shape.table
                col_w = ancho_tabla // n_cols
                for ci in range(n_cols):
                    tbl.columns[ci].width = Emu(col_w)
                fila_offset = 0
                if t.encabezados:
                    for ci, enc in enumerate(t.encabezados[:n_cols]):
                        cell = tbl.cell(0, ci)
                        cell.text = enc[:40]
                        cell.text_frame.paragraphs[0].font.bold = True
                        cell.text_frame.paragraphs[0].font.size = Pt(11)
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = RGBColor.from_string(TEMA.azul.lstrip("#"))
                        cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    fila_offset = 1
                for ri, fila in enumerate(t.filas[:n_filas]):
                    for ci, celda in enumerate(fila.celdas[:n_cols]):
                        cell = tbl.cell(ri + fila_offset, ci)
                        cell.text = celda[:40]
                        cell.text_frame.paragraphs[0].font.size = Pt(10)
                y_actual += alto_tabla + 0.4 * _EMU_POR_CM

        barra_inf = slide.shapes.add_shape(
            1,
            Emu(0), Emu(_ALTO_SLIDE - 0.3 * _EMU_POR_CM),
            Emu(_ANCHO_SLIDE), Emu(0.3 * _EMU_POR_CM),
        )
        barra_inf.fill.solid()
        barra_inf.fill.fore_color.rgb = RGBColor.from_string(TEMA.naranja.lstrip("#"))
        barra_inf.line.fill.background()
