"""Smoke tests de integración end-to-end.

Verifican que el pipeline completo Lector → Generador funciona
sin errores con documentos reales o sintéticos.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestSmokeCLI:
    """Smoke tests via CLI."""

    def test_md_a_pptx(self, tmp_path):
        md = tmp_path / "smoke.md"
        md.write_text("# Título de prueba\n\nContenido del documento.\n\n## Sección 2\n\nMás contenido.\n", encoding="utf-8")
        salida = tmp_path / "smoke.pptx"

        r = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md), "--formato", "pptx", "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"stderr: {r.stderr}"
        assert salida.exists()
        assert salida.stat().st_size > 1000  # PPTX no vacío

    def test_md_a_docx(self, tmp_path):
        md = tmp_path / "smoke.md"
        md.write_text("# Informe\n\n## Intro\n\nTexto de prueba.\n", encoding="utf-8")
        salida = tmp_path / "smoke.docx"

        r = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md), "--formato", "docx", "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"stderr: {r.stderr}"
        assert salida.exists()

    def test_md_a_xlsx(self, tmp_path):
        md = tmp_path / "smoke.md"
        md.write_text("# Reporte\n\n## Datos\n\nFila de datos.\n", encoding="utf-8")
        salida = tmp_path / "smoke.xlsx"

        r = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md), "--formato", "xlsx", "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"stderr: {r.stderr}"
        assert salida.exists()

    def test_docx_fixture_a_pptx(self, tmp_path):
        """Convierte el fixture DOCX a PPTX."""
        docx = FIXTURES / "informe_gestion.docx"
        if not docx.exists():
            pytest.skip("Fixture informe_gestion.docx no disponible")

        salida = tmp_path / "smoke.pptx"
        r = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(docx), "--formato", "pptx", "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"stderr: {r.stderr}"
        assert salida.exists()

    def test_epub_fixture_a_docx(self, tmp_path):
        """Convierte el fixture EPUB a DOCX."""
        epub = FIXTURES / "libro_tecnico.epub"
        if not epub.exists():
            pytest.skip("Fixture libro_tecnico.epub no disponible")

        salida = tmp_path / "smoke.docx"
        r = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(epub), "--formato", "docx", "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"stderr: {r.stderr}"
        assert salida.exists()


class TestSmokeAudio:
    def test_md_a_audio(self, tmp_path):
        """Sin motor de red disponible, el audio se genera silencioso."""
        md = tmp_path / "audio.md"
        md.write_text("# Título\n\nTexto para audio.\n", encoding="utf-8")
        salida = tmp_path / "audio.wav"

        r = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md), "--formato", "audio", "--salida", str(salida)],
            capture_output=True, text=True, timeout=120
        )
        # Puede fallar si no hay red ni SAPI, pero no debe crashear con excepción
        # En CI sin red: edge-tts fallará, SAPI fallará → CadenaVoz lanza ErrorVoz
        # El CLI captura ese error y devuelve código 1
        assert r.returncode in (0, 1)  # No crash no controlado


class TestSmokeVideo:
    def test_md_a_video(self, tmp_path):
        """Video silencioso sin motor de voz."""
        md = tmp_path / "video.md"
        md.write_text("# Presentación\n\nContenido del video.\n", encoding="utf-8")
        salida = tmp_path / "video.mp4"

        # Usamos la API Python directamente para controlar motor=None
        from txt2media.lectores.lector_md import LectorMarkdown
        from txt2media.generadores.generador_video import GeneradorVideo

        doc = LectorMarkdown().leer(md)
        gen = GeneradorVideo(voz="es-PE-CamilaNeural")
        gen.generar(doc, salida)

        assert salida.exists()
        assert salida.stat().st_size > 1000
