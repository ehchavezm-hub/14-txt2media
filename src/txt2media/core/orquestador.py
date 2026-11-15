"""Orquestador: procesa lista de archivos con cancelación."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable


class Orquestador:
    def __init__(self) -> None:
        self._cancelar = threading.Event()

    def cancelar(self) -> None:
        self._cancelar.set()

    def esta_cancelado(self) -> bool:
        return self._cancelar.is_set()

    def procesar(
        self,
        archivos: list[Path],
        formato: str,
        carpeta_salida: Path,
        callback_progreso: Callable[[int, int, str], None] | None = None,
    ) -> list[Path]:
        self._cancelar.clear()
        resultados: list[Path] = []
        total = len(archivos)

        for i, archivo in enumerate(archivos, start=1):
            if self.esta_cancelado():
                break
            if callback_progreso:
                callback_progreso(i, total, archivo.name)
            try:
                salida = self._convertir_uno(archivo, formato, carpeta_salida)
                resultados.append(salida)
            except Exception:
                pass

        return resultados

    def _convertir_uno(self, archivo: Path, formato: str, carpeta_salida: Path) -> Path:
        ext = archivo.suffix.lower()
        if ext == ".md":
            from txt2media.lectores.lector_md import LectorMarkdown
            lector = LectorMarkdown()
        elif ext == ".docx":
            from txt2media.lectores.lector_docx import LectorDOCX
            lector = LectorDOCX()
        elif ext == ".epub":
            from txt2media.lectores.lector_epub import LectorEPUB
            lector = LectorEPUB()
        elif ext == ".pdf":
            from txt2media.lectores.lector_pdf import LectorPDF
            lector = LectorPDF()
        else:
            raise ValueError(f"Extensión no soportada: {ext}")

        doc = lector.leer(archivo)
        salida = carpeta_salida / archivo.with_suffix(f".{formato}").name
        carpeta_salida.mkdir(parents=True, exist_ok=True)

        if formato == "pptx":
            from txt2media.generadores.generador_pptx import GeneradorPPTX
            GeneradorPPTX().generar(doc, salida, {})
        elif formato == "docx":
            from txt2media.generadores.generador_docx import GeneradorDOCX
            GeneradorDOCX().generar(doc, salida, {})
        elif formato == "xlsx":
            from txt2media.generadores.generador_xlsx import GeneradorXLSX
            GeneradorXLSX().generar(doc, salida, {})
        elif formato == "md":
            from txt2media.generadores.generador_md import GeneradorMD
            GeneradorMD().generar(doc, salida, {})
        elif formato == "html":
            from txt2media.generadores.generador_html import GeneradorHTML
            GeneradorHTML().generar(doc, salida, {})

        return salida
