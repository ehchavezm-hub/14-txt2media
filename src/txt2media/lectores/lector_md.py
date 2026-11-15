"""Lector Markdown usando markdown-it-py."""

from __future__ import annotations

from pathlib import Path

from txt2media.core.modelo import (
    Bloque, Documento, Seccion, TipoBloque,
)


class LectorMarkdown:
    def leer(self, ruta: Path) -> Documento:
        from markdown_it import MarkdownIt

        md = MarkdownIt()
        md.enable("table")
        texto = ruta.read_text(encoding="utf-8")
        tokens = md.parse(texto)
        return _tokens_a_documento(tokens, ruta.stem)


def _tokens_a_documento(tokens: list, titulo: str) -> Documento:
    secciones: list[Seccion] = []
    sec_actual = Seccion(titulo="", nivel=0, bloques=[])

    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if tok.type == "heading_open":
            nivel = int(tok.tag[1])
            contenido_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            texto_titulo = contenido_tok.content if contenido_tok else ""
            if sec_actual.bloques or sec_actual.titulo:
                secciones.append(sec_actual)
            sec_actual = Seccion(titulo=texto_titulo, nivel=nivel, bloques=[])
            i += 3
            continue

        elif tok.type == "paragraph_open":
            contenido_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            texto = contenido_tok.content if contenido_tok else ""
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.PARRAFO, contenido=texto))
            i += 3
            continue

        elif tok.type == "bullet_list_open":
            items: list[str] = []
            j = i + 1
            while j < len(tokens) and tokens[j].type != "bullet_list_close":
                if tokens[j].type == "inline":
                    items.append(tokens[j].content)
                j += 1
            sec_actual.bloques.append(
                Bloque(tipo=TipoBloque.LISTA, items_lista=items)
            )
            i = j + 1
            continue

        elif tok.type == "fence":
            sec_actual.bloques.append(
                Bloque(tipo=TipoBloque.CODIGO, contenido=tok.content, idioma_codigo=tok.info)
            )

        elif tok.type == "blockquote_open":
            j = i + 1
            texto_cita = ""
            while j < len(tokens) and tokens[j].type != "blockquote_close":
                if tokens[j].type == "inline":
                    texto_cita = tokens[j].content
                    break
                j += 1
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.CITA, contenido=texto_cita))

        elif tok.type == "hr":
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.SEPARADOR))

        i += 1

    if sec_actual.bloques or sec_actual.titulo:
        secciones.append(sec_actual)

    if not secciones:
        secciones.append(Seccion(titulo=titulo, nivel=1, bloques=[]))

    return Documento(titulo=titulo, secciones=secciones)
