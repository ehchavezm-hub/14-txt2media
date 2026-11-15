"""RenderizadorDiapositiva: genera imágenes 1920×1080 con Pillow."""

from __future__ import annotations

from pathlib import Path

from txt2media.core.modelo import Seccion, TipoBloque
from txt2media.core.tema import TEMA


class RenderizadorDiapositiva:
    ANCHO = 1920
    ALTO = 1080

    def __init__(self) -> None:
        self._fuente_titulo = None
        self._fuente_cuerpo = None

    def _cargar_fuentes(self):
        from PIL import ImageFont
        base = Path(__file__).parent.parent.parent.parent / "recursos" / "fuentes"
        try:
            self._fuente_titulo = ImageFont.truetype(str(base / "Figtree-Bold.ttf"), 60)
            self._fuente_cuerpo = ImageFont.truetype(str(base / "Figtree-Regular.ttf"), 36)
        except Exception:
            self._fuente_titulo = ImageFont.load_default()
            self._fuente_cuerpo = ImageFont.load_default()

    def render_portada(self, titulo: str, subtitulo: str = "") -> "Image":
        from PIL import Image, ImageDraw
        if not self._fuente_titulo:
            self._cargar_fuentes()
        img = Image.new("RGB", (self.ANCHO, self.ALTO), color=TEMA.azul)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, self.ALTO - 120), (self.ANCHO, self.ALTO)], fill=TEMA.naranja)
        self._texto_centrado(draw, titulo, self.ALTO // 2 - 60, self._fuente_titulo, "white")
        if subtitulo:
            self._texto_centrado(draw, subtitulo, self.ALTO // 2 + 40, self._fuente_cuerpo, "#E0E0E0")
        return img

    def render_seccion(self, sec: Seccion) -> "Image":
        from PIL import Image, ImageDraw
        from txt2media.core.modelo import TipoBloque
        if not self._fuente_titulo:
            self._cargar_fuentes()
        img = Image.new("RGB", (self.ANCHO, self.ALTO), color="white")
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (self.ANCHO, 120)], fill=TEMA.azul)
        if sec.titulo:
            draw.text((60, 30), sec.titulo[:80], fill="white", font=self._fuente_titulo)
        y = 160
        for bloque in sec.bloques:
            if y > self.ALTO - 80:
                break
            if bloque.tipo in (TipoBloque.PARRAFO, TipoBloque.CITA):
                texto = (bloque.contenido or "")[:200]
                draw.text((60, y), texto, fill="#1A1A1A", font=self._fuente_cuerpo)
                y += 60
            elif bloque.tipo == TipoBloque.LISTA and bloque.items_lista:
                for item in bloque.items_lista[:6]:
                    draw.text((80, y), f"• {item[:100]}", fill="#1A1A1A", font=self._fuente_cuerpo)
                    y += 50
        draw.rectangle([(0, self.ALTO - 8), (self.ANCHO, self.ALTO)], fill=TEMA.naranja)
        return img

    def _texto_centrado(self, draw, texto: str, y: int, fuente, color: str) -> None:
        try:
            bbox = draw.textbbox((0, 0), texto[:80], font=fuente)
            w = bbox[2] - bbox[0]
            x = (self.ANCHO - w) // 2
        except Exception:
            x = 60
        draw.text((x, y), texto[:80], fill=color, font=fuente)
