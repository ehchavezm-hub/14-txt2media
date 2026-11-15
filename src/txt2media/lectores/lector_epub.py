"""Lector EPUB usando zipfile + defusedxml + beautifulsoup4 (sin ebooklib AGPL)."""

from __future__ import annotations

import zipfile
from pathlib import Path, PurePosixPath

from txt2media.core.modelo import Bloque, Documento, Seccion, TipoBloque


class LectorEPUB:
    def leer(self, ruta: Path) -> Documento:
        with zipfile.ZipFile(str(ruta), "r") as zf:
            nombres = zf.namelist()
            opf_path = _encontrar_opf(zf, nombres)
            if not opf_path:
                return Documento(titulo=ruta.stem, secciones=[])
            spine_hrefs = _leer_spine(zf, opf_path)
            titulo_libro = _leer_titulo(zf, opf_path) or ruta.stem
            secciones: list[Seccion] = []
            for href in spine_hrefs:
                try:
                    datos = zf.read(href)
                except KeyError:
                    continue
                secs = _html_a_secciones(datos)
                secciones.extend(secs)

        if not secciones:
            secciones.append(Seccion(titulo=titulo_libro, nivel=1, bloques=[]))

        return Documento(titulo=titulo_libro, secciones=secciones)


def _encontrar_opf(zf: zipfile.ZipFile, nombres: list[str]) -> str | None:
    import defusedxml.ElementTree as ET

    container = "META-INF/container.xml"
    if container not in nombres:
        for n in nombres:
            if n.endswith(".opf"):
                return n
        return None
    datos = zf.read(container)
    root = ET.fromstring(datos)
    ns = {"cn": "urn:oasis:names:tc:opendocument:xmlns:container"}
    rootfile = root.find(".//cn:rootfile", ns)
    if rootfile is not None:
        return rootfile.get("full-path")
    return None


def _leer_spine(zf: zipfile.ZipFile, opf_path: str) -> list[str]:
    import defusedxml.ElementTree as ET

    datos = zf.read(opf_path)
    root = ET.fromstring(datos)
    ns_opf = "http://www.idpf.org/2007/opf"
    ns = {"opf": ns_opf}

    items: dict[str, str] = {}
    for item in root.findall(".//opf:item", ns):
        item_id = item.get("id", "")
        href = item.get("href", "")
        media_type = item.get("media-type", "")
        if "html" in media_type or href.endswith((".html", ".xhtml", ".htm")):
            items[item_id] = href

    spine_elem = root.find("opf:spine", ns)
    orden: list[str] = []
    if spine_elem is not None:
        for itemref in spine_elem.findall("opf:itemref", ns):
            idref = itemref.get("idref", "")
            if idref in items:
                orden.append(items[idref])
    else:
        orden = list(items.values())

    base = str(PurePosixPath(opf_path).parent)
    resultado: list[str] = []
    for href in orden:
        if base and base != ".":
            resultado.append(f"{base}/{href}")
        else:
            resultado.append(href)
    return resultado


def _leer_titulo(zf: zipfile.ZipFile, opf_path: str) -> str:
    import defusedxml.ElementTree as ET

    datos = zf.read(opf_path)
    root = ET.fromstring(datos)
    ns = {"dc": "http://purl.org/dc/elements/1.1/"}
    titulo_elem = root.find(".//dc:title", ns)
    return titulo_elem.text.strip() if titulo_elem is not None and titulo_elem.text else ""


def _html_a_secciones(datos: bytes) -> list[Seccion]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(datos, "lxml")
    secciones: list[Seccion] = []
    sec_actual = Seccion(titulo="", nivel=0, bloques=[])

    for elem in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "blockquote", "pre"]
    ):
        tag = elem.name
        texto = elem.get_text(separator=" ", strip=True)
        if not texto:
            continue

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            nivel = int(tag[1])
            if sec_actual.bloques or sec_actual.titulo:
                secciones.append(sec_actual)
            sec_actual = Seccion(titulo=texto, nivel=nivel, bloques=[])

        elif tag == "p":
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.PARRAFO, contenido=texto))

        elif tag in ("ul", "ol"):
            items = [li.get_text(strip=True) for li in elem.find_all("li")]
            if items:
                sec_actual.bloques.append(
                    Bloque(tipo=TipoBloque.LISTA, items_lista=items)
                )

        elif tag == "blockquote":
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.CITA, contenido=texto))

        elif tag == "pre":
            sec_actual.bloques.append(Bloque(tipo=TipoBloque.CODIGO, contenido=texto))

    if sec_actual.bloques or sec_actual.titulo:
        secciones.append(sec_actual)

    return secciones
