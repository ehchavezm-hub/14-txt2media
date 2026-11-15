"""Generador Markdown enriquecido con colores inline y formato rico."""

from __future__ import annotations

import re
from pathlib import Path

from txt2media.core.modelo import Documento, Seccion, TipoBloque


def _texto_seccion(sec: Seccion) -> str:
    """Extrae texto plano de los bloques de una sección."""
    partes = []
    for bloque in sec.bloques:
        if bloque.tipo == TipoBloque.PARRAFO:
            partes.append(bloque.contenido)
        elif bloque.tipo == TipoBloque.LISTA:
            partes.extend(bloque.items_lista)
        elif bloque.tipo == TipoBloque.CAPTION:
            partes.append(bloque.contenido)
        elif bloque.tipo == TipoBloque.TABLA and bloque.tabla:
            for fila in bloque.tabla.filas:
                partes.append(" | ".join(fila.celdas))
    return "\n\n".join(partes)


class GeneradorMD:
    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        salida.parent.mkdir(parents=True, exist_ok=True)
        contenido = self._construir(doc)
        tmp = salida.with_suffix(".tmp")
        tmp.write_text(contenido, encoding="utf-8")
        import os
        os.replace(str(tmp), str(salida))
        return salida

    def _construir(self, doc: Documento) -> str:
        lines: list[str] = []

        # Portada
        lines.append(f'<div style="color:#4E79A7;font-size:2em;font-weight:bold;">')
        lines.append(f"{doc.titulo}")
        lines.append("</div>")
        if doc.autor:
            lines.append(f'<div style="color:#7A7A9A;font-size:0.9em;">{doc.autor}</div>')
        lines.append("")
        lines.append("---")
        lines.append("")

        # Índice
        lines.append("## Contenido")
        lines.append("")
        for i, sec in enumerate(doc.secciones, 1):
            titulo = sec.titulo or f"Sección {i}"
            anchor = re.sub(r"[^a-z0-9]+", "-", titulo.lower()).strip("-")
            lines.append(f"{i}. [{titulo}](#{anchor})")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Secciones
        for i, sec in enumerate(doc.secciones, 1):
            titulo = sec.titulo or f"Sección {i}"
            anchor = re.sub(r"[^a-z0-9]+", "-", titulo.lower()).strip("-")
            lines.append(f'## <span id="{anchor}" style="color:#4E79A7;">{titulo}</span>')
            lines.append("")
            for bloque in sec.bloques:
                if bloque.tipo == TipoBloque.PARRAFO:
                    texto = bloque.contenido.strip()
                    if texto:
                        if bloque.negrita and bloque.cursiva:
                            texto = f"***{texto}***"
                        elif bloque.negrita:
                            texto = f"**{texto}**"
                        elif bloque.cursiva:
                            texto = f"*{texto}*"
                        lines.append(self._enriquecer(texto))
                        lines.append("")
                elif bloque.tipo == TipoBloque.LISTA:
                    for item in bloque.items_lista:
                        lines.append(f"- {item}")
                    lines.append("")
                elif bloque.tipo == TipoBloque.CAPTION:
                    lines.append(f'<small style="color:#7A7A9A;">_{bloque.contenido}_</small>')
                    lines.append("")
                elif bloque.tipo == TipoBloque.TABLA and bloque.tabla:
                    t = bloque.tabla
                    if t.encabezados:
                        lines.append("| " + " | ".join(t.encabezados) + " |")
                        lines.append("|" + "|".join(["---"] * len(t.encabezados)) + "|")
                        for fila in t.filas:
                            lines.append("| " + " | ".join(fila.celdas) + " |")
                    elif t.filas:
                        # Sin encabezados explícitos: usar primera fila como cabecera
                        primera = t.filas[0]
                        lines.append("| " + " | ".join(primera.celdas) + " |")
                        lines.append("|" + "|".join(["---"] * len(primera.celdas)) + "|")
                        for fila in t.filas[1:]:
                            lines.append("| " + " | ".join(fila.celdas) + " |")
                    lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _enriquecer(self, texto: str) -> str:
        texto = re.sub(r"\b([A-Z]{2,})\b",
                       r'<span style="color:#F28E2B;font-weight:bold;">\1</span>', texto)
        texto = re.sub(r"\b(\d+[\.,]?\d*\s*%)", r"**\1**", texto)
        return texto
