"""Tests para el CLI convdoc."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIBasico:
    def test_help_no_lanza_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_help_muestra_txt2media(self):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main", "--help"],
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        assert "txt2media" in output.lower()

    def test_version_muestra_numero(self):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main", "--version"],
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        # Debe contener algo como "0.1.0"
        assert any(c.isdigit() for c in output)

    def test_sin_argumentos_no_crashea(self):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main"],
            capture_output=True, text=True
        )
        # Puede devolver 0 (ayuda) o 2 (argparse error), pero no excepción no controlada
        assert result.returncode in (0, 1, 2)

    def test_archivo_inexistente_devuelve_error(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(tmp_path / "no_existe.md"),
             "--formato", "pptx", "--salida", str(tmp_path / "out.pptx")],
            capture_output=True, text=True
        )
        assert result.returncode != 0
        output = result.stdout + result.stderr
        assert "no_existe" in output or "error" in output.lower() or "Error" in output

    def test_subcomando_convertir_existe(self):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main", "convertir", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_subcomando_clave_existe(self):
        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main", "clave", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0


class TestCLIConvertir:
    def test_convierte_md_a_docx(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Título\n\nContenido de prueba.\n", encoding="utf-8")
        salida = tmp_path / "out.docx"

        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md),
             "--formato", "docx",
             "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0
        assert salida.exists()

    def test_convierte_md_a_xlsx(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Reporte\n\nDatos de prueba.\n", encoding="utf-8")
        salida = tmp_path / "out.xlsx"

        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md),
             "--formato", "xlsx",
             "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0
        assert salida.exists()

    def test_convierte_md_a_pptx(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Presentación\n\nDiapositiva de prueba.\n", encoding="utf-8")
        salida = tmp_path / "out.pptx"

        result = subprocess.run(
            [sys.executable, "-m", "txt2media.cli.main",
             "convertir", str(md),
             "--formato", "pptx",
             "--salida", str(salida)],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0
        assert salida.exists()
