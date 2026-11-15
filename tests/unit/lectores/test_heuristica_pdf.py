"""Tests para heuristica_pdf — detección de estructura jerárquica en PDFs."""

import pytest

from txt2media.lectores.heuristica_pdf import (
    TextoConFuente,
    calcular_mediana_fuente,
    detectar_dos_columnas,
    detectar_headers_footers,
    detectar_nivel_titulo,
    ordenar_dos_columnas,
)


def _texto(texto, tamano=12.0, negrita=False, x0=72, y0=100, x1=400, y1=120, pagina=1):
    return TextoConFuente(
        texto=texto,
        tamano_fuente=tamano,
        negrita=negrita,
        x0=x0, y0=y0, x1=x1, y1=y1,
        pagina=pagina,
    )


class TestCalcularMedianaFuente:
    def test_lista_vacia_devuelve_12(self):
        assert calcular_mediana_fuente([]) == 12.0

    def test_fuentes_uniformes(self):
        textos = [_texto("texto", tamano=10.0) for _ in range(5)]
        assert calcular_mediana_fuente(textos) == 10.0

    def test_mediana_con_outlier(self):
        # 5 textos de 10pt y 1 título de 24pt → mediana debería ser 10
        textos = [_texto("texto", tamano=10.0) for _ in range(5)]
        textos.append(_texto("TÍTULO", tamano=24.0))
        assert calcular_mediana_fuente(textos) == 10.0

    def test_fuente_cero_ignorada(self):
        textos = [_texto("a", tamano=0.0), _texto("b", tamano=12.0)]
        assert calcular_mediana_fuente(textos) == 12.0


class TestDetectarNivelTitulo:
    def test_ratio_mayor_15_es_nivel_1(self):
        t = _texto("Gran Título", tamano=20.0)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) == 1

    def test_ratio_mayor_13_es_nivel_2(self):
        t = _texto("Sección", tamano=16.0)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) == 2

    def test_ratio_mayor_umbral_es_nivel_3(self):
        t = _texto("Subsección", tamano=14.0)  # 14/12 = 1.167 >= 1.15
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) == 3

    def test_negrita_sin_ratio_es_nivel_4(self):
        t = _texto("Párrafo negrita", tamano=12.0, negrita=True)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) == 4

    def test_texto_normal_no_es_titulo(self):
        t = _texto("Texto normal de un párrafo", tamano=12.0, negrita=False)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) is None

    def test_numeracion_simple_es_titulo(self):
        t = _texto("1. Introducción", tamano=12.0)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) is not None

    def test_numeracion_subnivel_es_titulo(self):
        t = _texto("1.1 Objetivos", tamano=12.0)
        nivel = detectar_nivel_titulo(t, mediana_fuente=12.0)
        assert nivel is not None
        assert nivel > 1  # subnivel mayor que el nivel padre

    def test_capitulo_es_titulo(self):
        t = _texto("Capítulo 3", tamano=12.0)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) is not None

    def test_texto_vacio_es_none(self):
        t = _texto("", tamano=12.0)
        assert detectar_nivel_titulo(t, mediana_fuente=12.0) is None


class TestDetectarDosColumnas:
    def _textos_dos_columnas(self, ancho=612.0):
        """Genera textos distribuidos en dos columnas (izq < mitad, der > mitad)."""
        mitad = ancho / 2
        izquierda = [_texto(f"izq {i}", x0=72, x1=mitad - 20) for i in range(10)]
        derecha = [_texto(f"der {i}", x0=mitad + 20, x1=ancho - 72) for i in range(10)]
        return izquierda + derecha

    def test_detecta_dos_columnas(self):
        textos = self._textos_dos_columnas()
        assert detectar_dos_columnas(textos, 612.0) is True

    def test_una_columna_no_detectada(self):
        textos = [_texto(f"p{i}", x0=72, x1=540) for i in range(20)]
        assert detectar_dos_columnas(textos, 612.0) is False

    def test_lista_vacia_no_detectada(self):
        assert detectar_dos_columnas([], 612.0) is False

    def test_ancho_cero_no_detectado(self):
        textos = [_texto("texto", x0=72, x1=400)]
        assert detectar_dos_columnas(textos, 0.0) is False


class TestOrdenarDosColumnas:
    def test_orden_lectura_dos_columnas(self):
        """Columna izquierda debe aparecer antes que columna derecha."""
        mitad = 306.0
        # Columna derecha tiene y0 más arriba (menor) que columna izquierda
        t_der_top = _texto("Der arriba", x0=mitad + 10, x1=540, y0=50)
        t_izq_bottom = _texto("Izq abajo", x0=72, x1=mitad - 10, y0=200)
        t_izq_top = _texto("Izq arriba", x0=72, x1=mitad - 10, y0=50)

        resultado = ordenar_dos_columnas([t_der_top, t_izq_bottom, t_izq_top], 612.0)

        # La columna izquierda va primero completa, sin importar posición vertical
        indices_izq = [i for i, t in enumerate(resultado) if "Izq" in t.texto]
        indices_der = [i for i, t in enumerate(resultado) if "Der" in t.texto]
        assert max(indices_izq) < min(indices_der)

    def test_orden_vertical_dentro_de_columna(self):
        """Dentro de cada columna, el texto va de arriba hacia abajo."""
        mitad = 306.0
        t_abajo = _texto("Izq abajo", x0=72, x1=mitad - 10, y0=200)
        t_arriba = _texto("Izq arriba", x0=72, x1=mitad - 10, y0=50)

        resultado = ordenar_dos_columnas([t_abajo, t_arriba], 612.0)
        textos = [t.texto for t in resultado]
        assert textos.index("Izq arriba") < textos.index("Izq abajo")


class TestDetectarHeadersFooters:
    def test_detecta_repeticion_en_misma_posicion(self):
        """Texto que aparece en 3+ páginas en la misma posición es header/footer."""
        paginas = []
        for i in range(5):
            paginas.append([
                _texto("Pie de página - COSAPI", y0=750),
                # Contenido único en posición diferente cada página
                _texto(f"Párrafo único de la página {i}", y0=100 + i * 50),
            ])
        headers = detectar_headers_footers(paginas, min_repeticiones=3)
        assert "Pie de página - COSAPI" in headers
        for i in range(5):
            assert f"Párrafo único de la página {i}" not in headers

    def test_no_detecta_con_pocas_paginas(self):
        """Con menos páginas que el mínimo, no detecta nada."""
        paginas = [
            [_texto("Pie", y0=750)],
            [_texto("Pie", y0=750)],
        ]
        headers = detectar_headers_footers(paginas, min_repeticiones=3)
        assert len(headers) == 0

    def test_lista_vacia_devuelve_vacio(self):
        assert detectar_headers_footers([]) == set()
