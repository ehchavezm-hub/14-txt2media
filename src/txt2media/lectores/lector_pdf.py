"""Lector PDF usando pdfplumber con heurísticas de estructura."""

from __future__ import annotations

from pathlib import Path

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque


_UMBRAL_TITULO_PT = 14.0


class LectorPDF:
    def leer(self, ruta: Path) -> Documento:
        import pdfplumber

        secciones: list[Seccion] = []
        sec_actual = Seccion(titulo=ruta.stem, nivel=0, bloques=[])

        with pdfplumber.open(str(ruta)) as pdf:
            for pagina in pdf.pages:
                palabras = pagina.extract_words(extra_attrs=["size", "fontname"])
                lineas = _agrupar_lineas(palabras)
                for linea in lineas:
                    texto = linea["texto"].strip()
                    if not texto:
                        continue
                    if linea["es_titulo"]:
                        nivel = 1 if linea["tamano"] >= _UMBRAL_TITULO_PT + 4 else 2
                        if sec_actual.bloques or sec_actual.titulo != ruta.stem:
                            secciones.append(sec_actual)
                        sec_actual = Seccion(titulo=texto, nivel=nivel, bloques=[])
                    else:
                        if texto.startswith(("• ", "- ", "* ")):
                            item = texto[2:].strip()
                            if sec_actual.bloques and sec_actual.bloques[-1].tipo == TipoBloque.LISTA:
                                sec_actual.bloques[-1].items_lista.append(item)
                            else:
                                sec_actual.bloques.append(
                                    Bloque(tipo=TipoBloque.LISTA, items_lista=[item])
                                )
                        else:
                            sec_actual.bloques.append(
                                Bloque(tipo=TipoBloque.PARRAFO, contenido=texto)
                            )

        if sec_actual.bloques or sec_actual.titulo != ruta.stem:
            secciones.append(sec_actual)

        if not secciones:
            secciones.append(Seccion(titulo=ruta.stem, nivel=1, bloques=[]))

        return Documento(titulo=ruta.stem, secciones=secciones)


def _agrupar_lineas(palabras: list[dict]) -> list[dict]:
    if not palabras:
        return []

    lineas: list[dict] = []
    linea_actual: list[dict] = [palabras[0]]

    for palabra in palabras[1:]:
        ultima = linea_actual[-1]
        misma_linea = abs(palabra.get("top", 0) - ultima.get("top", 0)) < 3
        if misma_linea:
            linea_actual.append(palabra)
        else:
            lineas.append(_construir_linea(linea_actual))
            linea_actual = [palabra]

    if linea_actual:
        lineas.append(_construir_linea(linea_actual))

    return lineas


def _construir_linea(palabras: list[dict]) -> dict:
    texto = " ".join(p.get("text", "") for p in palabras)
    tamanos = [p.get("size", 0) for p in palabras if p.get("size")]
    tamano = max(tamanos) if tamanos else 0
    es_titulo = tamano >= _UMBRAL_TITULO_PT
    return {"texto": texto, "tamano": tamano, "es_titulo": es_titulo}
