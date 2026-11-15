"""Modelo de datos central de txt2media."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class TipoBloque(Enum):
    PARRAFO = "parrafo"
    TITULO = "titulo"
    LISTA = "lista"
    TABLA = "tabla"
    IMAGEN = "imagen"
    CODIGO = "codigo"
    CITA = "cita"
    SEPARADOR = "separador"
    CAPTION = "caption"       # pie de figura/tabla
    NOTA_PIE = "nota_pie"     # footnote (referencia, no flujo principal)


@dataclass
class FilaTabla:
    celdas: list[str] = field(default_factory=list)
    es_encabezado: bool = False


@dataclass
class Tabla:
    encabezados: list[str] = field(default_factory=list)
    filas: list[FilaTabla] = field(default_factory=list)


@dataclass
class Imagen:
    ruta: Path | None = None
    datos: bytes | None = None
    alt: str = ""
    ancho: int | None = None
    alto: int | None = None


@dataclass
class Bloque:
    tipo: TipoBloque = TipoBloque.PARRAFO
    contenido: str = ""
    nivel: int = 1
    items_lista: list[str] = field(default_factory=list)
    tabla: Tabla | None = None
    imagen: Imagen | None = None
    idioma_codigo: str = ""
    negrita: bool = False
    cursiva: bool = False


@dataclass
class Seccion:
    nivel: int = 1
    titulo: str = ""
    bloques: list[Bloque] = field(default_factory=list)


@dataclass
class Documento:
    titulo: str = ""
    autor: str = ""
    idioma: str = "es"
    secciones: list[Seccion] = field(default_factory=list)
    ruta_origen: Path | None = None
    metadatos: dict = field(default_factory=dict)
