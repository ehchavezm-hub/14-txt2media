"""Tests para RenderizadorDiapositiva (Pillow, 1920x1080)."""

import pytest
from pathlib import Path
from PIL import Image

from txt2media.core.renderizador import RenderizadorDiapositiva, ConfigDiapositiva


PALETA = {
    "primario": "#4E79A7",
    "acento": "#F28E2B",
    "texto": "#2B2B2B",
    "fondo": "#FFFFFF",
    "superficie": "#F5F6F8",
    "borde": "#BAB0AC",
}


class TestConfigDiapositiva:
    def test_config_por_defecto(self):
        cfg = ConfigDiapositiva()
        assert cfg.ancho == 1920
        assert cfg.alto == 1080
        assert cfg.margen > 0

    def test_config_personalizada(self):
        cfg = ConfigDiapositiva(ancho=1280, alto=720)
        assert cfg.ancho == 1280
        assert cfg.alto == 720


class TestRenderizadorDiapositiva:
    def setup_method(self):
        self.r = RenderizadorDiapositiva(paleta=PALETA)

    def test_diapositiva_titulo_devuelve_imagen_1920x1080(self, tmp_path):
        img = self.r.diapositiva_titulo(
            titulo="Informe Técnico 2026",
            subtitulo="COSAPI S.A.",
        )
        assert isinstance(img, Image.Image)
        assert img.width == 1920
        assert img.height == 1080

    def test_modo_rgb(self, tmp_path):
        img = self.r.diapositiva_titulo("T", "S")
        assert img.mode == "RGB"

    def test_diapositiva_contenido_devuelve_imagen(self):
        img = self.r.diapositiva_contenido(
            titulo="2. Avance de Obra",
            cuerpo="Los trabajos de estructuras han alcanzado un avance del 75%.",
        )
        assert isinstance(img, Image.Image)
        assert img.size == (1920, 1080)

    def test_diapositiva_lista_devuelve_imagen(self):
        img = self.r.diapositiva_lista(
            titulo="Indicadores",
            items=["Avance: 78%", "Costo/m²: S/ 1,752", "Días: 87"],
        )
        assert isinstance(img, Image.Image)
        assert img.size == (1920, 1080)

    def test_diapositiva_tabla_devuelve_imagen(self):
        from txt2media.core.modelo import Tabla, FilaTabla
        tabla = Tabla(
            encabezados=["Partida", "Avance"],
            filas=[
                FilaTabla(celdas=["Concreto", "75%"]),
                FilaTabla(celdas=["Acero", "80%"]),
            ],
            confianza=1.0,
        )
        img = self.r.diapositiva_tabla(titulo="Tabla", tabla=tabla)
        assert isinstance(img, Image.Image)
        assert img.size == (1920, 1080)

    def test_guardar_como_png(self, tmp_path):
        img = self.r.diapositiva_titulo("Test", "Sub")
        ruta = tmp_path / "diap.png"
        img.save(str(ruta))
        assert ruta.exists()
        assert ruta.stat().st_size > 0

    def test_color_fondo_aplicado(self):
        """El fondo fuera de la banda debe ser blanco (#FFFFFF)."""
        img = self.r.diapositiva_titulo("T", "S")
        # La banda ocupa el tercio superior; el pixel en zona central debe ser fondo blanco
        y_centro = int(img.height * 0.6)
        px = img.getpixel((10, y_centro))
        assert px[:3] == (255, 255, 255)

    def test_numero_diapositiva_en_pie(self):
        """El pie de página debe poder mostrar número de diapositiva."""
        img = self.r.diapositiva_contenido(
            titulo="Test",
            cuerpo="Contenido",
            numero=3,
            total=10,
        )
        assert isinstance(img, Image.Image)

    def test_texto_largo_no_lanza_error(self):
        """Texto que excede el área disponible no debe lanzar excepción."""
        texto_largo = "Lorem ipsum dolor sit amet, " * 50
        img = self.r.diapositiva_contenido(
            titulo="Título de prueba con texto muy largo en el cuerpo",
            cuerpo=texto_largo,
        )
        assert isinstance(img, Image.Image)
