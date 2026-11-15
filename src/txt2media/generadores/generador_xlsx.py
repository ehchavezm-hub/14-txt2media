"""Generador XLSX usando openpyxl."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from txt2media.core.modelo import Documento, TipoBloque
from txt2media.core.tema import TEMA


class GeneradorXLSX:
    def generar(self, doc: Documento, salida: Path, opciones: dict) -> None:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        ws_indice = wb.active
        ws_indice.title = "Índice"
        ws_indice["A1"] = doc.titulo
        ws_indice["A1"].font = Font(bold=True, size=14)

        for i, sec in enumerate(doc.secciones, start=1):
            if not sec.titulo and not sec.bloques:
                continue
            ws_indice.cell(row=i + 1, column=1, value=sec.titulo or f"Sección {i}")

            nombre_hoja = _nombre_hoja_seguro(sec.titulo or f"sec_{i}", i)
            ws = wb.create_sheet(title=nombre_hoja)

            if sec.titulo:
                ws["A1"] = sec.titulo
                ws["A1"].font = Font(bold=True, size=13, color="FFFFFF")
                ws["A1"].fill = PatternFill(
                    "solid", fgColor=TEMA.azul.lstrip("#")
                )
                fila = 3
            else:
                fila = 1

            for bloque in sec.bloques:
                if bloque.tipo == TipoBloque.PARRAFO and bloque.contenido:
                    ws.cell(row=fila, column=1, value=bloque.contenido)
                    ws.cell(row=fila, column=1).alignment = Alignment(wrap_text=True)
                    ws.row_dimensions[fila].height = 30
                    fila += 1

                elif bloque.tipo == TipoBloque.LISTA and bloque.items_lista:
                    for item in bloque.items_lista:
                        ws.cell(row=fila, column=1, value=f"• {item}")
                        fila += 1

                elif bloque.tipo == TipoBloque.TABLA and bloque.tabla:
                    t = bloque.tabla
                    if t.encabezados:
                        for j, enc in enumerate(t.encabezados, start=1):
                            cell = ws.cell(row=fila, column=j, value=enc)
                            cell.font = Font(bold=True, color="FFFFFF")
                            cell.fill = PatternFill(
                                "solid", fgColor=TEMA.azul.lstrip("#")
                            )
                        fila += 1
                    for fil in t.filas:
                        for j, celda in enumerate(fil.celdas, start=1):
                            ws.cell(row=fila, column=j, value=celda)
                        fila += 1
                    fila += 1

                elif bloque.tipo == TipoBloque.SEPARADOR:
                    fila += 1

            for col in ws.columns:
                max_len = max(
                    (len(str(c.value)) for c in col if c.value), default=10
                )
                ws.column_dimensions[get_column_letter(col[0].column)].width = min(
                    max_len + 4, 60
                )

        salida.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=salida.parent)
        os.close(fd)
        try:
            wb.save(tmp)
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise


def _nombre_hoja_seguro(nombre: str, indice: int) -> str:
    prohibidos = r"\/*?:[]"
    for c in prohibidos:
        nombre = nombre.replace(c, "")
    nombre = nombre[:28].strip()
    if not nombre:
        nombre = f"Hoja{indice}"
    return nombre
