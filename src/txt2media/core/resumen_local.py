"""MotorResumenLocal: resumen extractivo TF sin red."""

from __future__ import annotations

import re
from collections import Counter

from txt2media.core.modelo import Documento, TipoBloque


class MotorResumenLocal:
    """Resumen extractivo por frecuencia de términos. Sin red."""

    NIVELES = {"breve": 3, "medio": 6, "completo": 10}

    def resumir(self, doc: Documento, nivel: str = "medio") -> str:
        n_oraciones = self.NIVELES.get(nivel, 6)
        texto = self._extraer_texto(doc)
        oraciones = self._tokenizar_oraciones(texto)
        if len(oraciones) <= n_oraciones:
            return texto
        puntuaciones = self._puntuar(oraciones)
        mejores = sorted(
            range(len(oraciones)),
            key=lambda i: puntuaciones[i],
            reverse=True,
        )[:n_oraciones]
        mejores_ordenados = sorted(mejores)
        return " ".join(oraciones[i] for i in mejores_ordenados)

    def _extraer_texto(self, doc: Documento) -> str:
        partes: list[str] = [doc.titulo]
        for sec in doc.secciones:
            if sec.titulo:
                partes.append(sec.titulo)
            for bloque in sec.bloques:
                if bloque.tipo in (TipoBloque.PARRAFO, TipoBloque.CITA):
                    if bloque.contenido:
                        partes.append(bloque.contenido)
        return " ".join(p for p in partes if p)

    def _tokenizar_oraciones(self, texto: str) -> list[str]:
        oraciones = re.split(r"(?<=[.!?])\s+", texto)
        return [o.strip() for o in oraciones if o.strip()]

    def _puntuar(self, oraciones: list[str]) -> list[float]:
        palabras_todas = re.findall(r"\w+", " ".join(oraciones).lower())
        stopwords = {"el", "la", "los", "las", "un", "una", "de", "del",
                     "en", "y", "a", "que", "es", "se", "con", "por", "para"}
        frecuencias = Counter(w for w in palabras_todas if w not in stopwords and len(w) > 3)
        puntuaciones = []
        for oracion in oraciones:
            palabras = re.findall(r"\w+", oracion.lower())
            score = sum(frecuencias.get(p, 0) for p in palabras if p not in stopwords)
            puntuaciones.append(score / max(len(palabras), 1))
        return puntuaciones
