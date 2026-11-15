"""Generador DOCX usando python-docx."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from txt2media.core.modelo import Documento, TipoBloque


class GeneradorDOCX:
    def generar(self, doc: Documento, salida: Path, opciones: dict) -> None:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.oxml.ns import qn

        d = Document()
        d.add_heading(doc.titulo, level=0)

        for sec in doc.secciones:
            if sec.titulo:
                d.add_heading(sec.titulo, level=min(sec.nivel, 9))
            for bloque in sec.bloques:
                if bloque.tipo == TipoBloque.PARRAFO and bloque.contenido:
                    d.add_paragraph(bloque.contenido)
                elif bloque.tipo == TipoBloque.LISTA and bloque.items_lista:
                    for item in bloque.items_lista:
                        d.add_paragraph(item, style="List Bullet")
                elif bloque.tipo == TipoBloque.TABLA and bloque.tabla:
                    t = bloque.tabla
                    n_cols = max(len(t.encabezados), max((len(f.celdas) for f in t.filas), default=0))
                    if n_cols == 0:
                        continue
                    tabla_obj = d.add_table(rows=1, cols=n_cols)
                    tabla_obj.style = "Table Grid"
                    hdr = tabla_obj.rows[0].cells
                    for i, enc in enumerate(t.encabezados[:n_cols]):
                        hdr[i].text = enc
                        hdr[i].paragraphs[0].runs[0].bold = True
                    for fila in t.filas:
                        fila_obj = tabla_obj.add_row().cells
                        for i, celda in enumerate(fila.celdas[:n_cols]):
                            fila_obj[i].text = celda
                elif bloque.tipo == TipoBloque.CODIGO and bloque.contenido:
                    p = d.add_paragraph(bloque.contenido)
                    p.style = "Normal"
                    for run in p.runs:
                        run.font.name = "Courier New"
                        run.font.size = Pt(9)
                elif bloque.tipo == TipoBloque.CITA and bloque.contenido:
                    p = d.add_paragraph(bloque.contenido)
                    try:
                        p.style = "Quote"
                    except Exception:
                        pass
                elif bloque.tipo == TipoBloque.SEPARADOR:
                    d.add_paragraph("─" * 40)

        salida.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".docx", dir=salida.parent)
        os.close(fd)
        try:
            d.save(tmp)
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
