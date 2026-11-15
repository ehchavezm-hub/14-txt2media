"""Generador Markdown enriquecido con colores inline y formato rico."""

from __future__ import annotations

import re
from pathlib import Path

from txt2media.core.modelo import Documento, Seccion


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
            for parrafo in self._dividir_parrafos(sec.texto):
                if parrafo.strip():
                    lines.append(self._enriquecer(parrafo.strip()))
                    lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _dividir_parrafos(self, texto: str) -> list[str]:
        return [p for p in texto.split("\n\n") if p.strip()]

    def _enriquecer(self, texto: str) -> str:
        # Resaltar términos en mayúsculas (siglas)
        texto = re.sub(r"\b([A-Z]{2,})\b", r'<span style="color:#F28E2B;font-weight:bold;">\1</span>', texto)
        # Resaltar números con unidades
        texto = re.sub(r"\b(\d+[\.,]?\d*\s*%)", r'**\1**', texto)
        return texto
