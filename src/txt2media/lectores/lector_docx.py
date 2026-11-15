"""Lector DOCX usando python-docx."""

from __future__ import annotations

from pathlib import Path

from txt2media.core.modelo import (
    Bloque, Documento, FilaTabla, Seccion, Tabla, TipoBloque,
)


class LectorDOCX:
    def leer(self, ruta: Path) -> Documento:
        from docx import Document
        from docx.oxml.ns import qn

        doc = Document(str(ruta))
        secciones: list[Seccion] = []
        sec_actual = Seccion(titulo=ruta.stem, nivel=0, bloques=[])

        for elem in doc.element.body:
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if tag == "p":
                from docx.text.paragraph import Paragraph
                p = Paragraph(elem, doc)
                texto = p.text.strip()
                if not texto:
                    continue
                estilo = (p.style.name or "").lower()
                if estilo.startswith("heading"):
                    try:
                        nivel = int(estilo.split()[-1])
                    except ValueError:
                        nivel = 1
                    if sec_actual.bloques or sec_actual.titulo != ruta.stem:
                        secciones.append(sec_actual)
                    sec_actual = Seccion(titulo=texto, nivel=nivel, bloques=[])
                elif estilo.startswith("list"):
                    if sec_actual.bloques and sec_actual.bloques[-1].tipo == TipoBloque.LISTA:
                        sec_actual.bloques[-1].items_lista.append(texto)
                    else:
                        sec_actual.bloques.append(
                            Bloque(tipo=TipoBloque.LISTA, items_lista=[texto])
                        )
                else:
                    sec_actual.bloques.append(
                        Bloque(tipo=TipoBloque.PARRAFO, contenido=texto)
                    )

            elif tag == "tbl":
                from docx.table import Table
                tabla_obj = Table(elem, doc)
                filas: list[FilaTabla] = []
                encabezados: list[str] = []
                for i, fila in enumerate(tabla_obj.rows):
                    celdas = [c.text.strip() for c in fila.cells]
                    if i == 0:
                        encabezados = celdas
                    else:
                        filas.append(FilaTabla(celdas=celdas))
                sec_actual.bloques.append(
                    Bloque(
                        tipo=TipoBloque.TABLA,
                        tabla=Tabla(encabezados=encabezados, filas=filas),
                    )
                )

        if sec_actual.bloques or sec_actual.titulo != ruta.stem:
            secciones.append(sec_actual)

        if not secciones:
            secciones.append(Seccion(titulo=ruta.stem, nivel=1, bloques=[]))

        return Documento(titulo=ruta.stem, secciones=secciones)
