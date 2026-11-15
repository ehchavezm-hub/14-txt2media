"""Tests para utils.recursos y utils.rutas."""

import os
import zipfile
from pathlib import Path

import pytest

from txt2media.utils.recursos import get_recurso, get_recurso_existente
from txt2media.utils.rutas import get_datos_dir, ruta_salida, sanear_nombre_archivo
from txt2media.utils.seguridad import RutaMaliciosaError, ZipBombaError, validar_zip


# --- recursos.py ---


def test_get_recurso_devuelve_path() -> None:
    ruta = get_recurso("tema_tableau_figtree.json")
    assert isinstance(ruta, Path)


def test_get_recurso_encuentra_tema_por_defecto() -> None:
    ruta = get_recurso("tema_tableau_figtree.json")
    assert ruta.exists(), f"El archivo de tema no existe en: {ruta}"


def test_get_recurso_existente_lanza_si_no_existe() -> None:
    with pytest.raises(FileNotFoundError):
        get_recurso_existente("archivo_que_no_existe_jamas.xyz")


# --- rutas.py ---


def test_get_datos_dir_devuelve_path_existente(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)
    datos = get_datos_dir()
    assert datos.exists()
    assert datos.is_dir()


def test_sanear_nombre_sin_caracteres_invalidos() -> None:
    assert sanear_nombre_archivo("Informe_2026") == "Informe_2026"


def test_sanear_nombre_reemplaza_invalidos() -> None:
    resultado = sanear_nombre_archivo("Informe<2026>:Final")
    assert "<" not in resultado
    assert ">" not in resultado
    assert ":" not in resultado


def test_sanear_nombre_tildes_y_enie() -> None:
    # Las tildes y la ñ son válidas en nombres de Windows
    assert sanear_nombre_archivo("Análisis_técnico_año") == "Análisis_técnico_año"


def test_sanear_nombre_reservado_windows() -> None:
    resultado = sanear_nombre_archivo("CON")
    assert resultado != "CON"


def test_ruta_salida_estructura_correcta() -> None:
    ruta = ruta_salida("MiInforme", "docx", "2026-01-15_1030")
    assert ruta.parts[0] == "Salida"
    assert ruta.parts[1] == "MiInforme"
    assert ruta.parts[2] == "2026-01-15_1030"
    assert ruta.name == "MiInforme.docx"


# --- seguridad.py ---


def test_validar_zip_acepta_zip_limpio(tmp_path: Path) -> None:
    ruta_zip = tmp_path / "limpio.zip"
    with zipfile.ZipFile(ruta_zip, "w") as zf:
        zf.writestr("tema.json", '{"nombre": "test"}')
    validar_zip(ruta_zip)  # No debe lanzar


def test_validar_zip_rechaza_ruta_maliciosa(tmp_path: Path) -> None:
    ruta_zip = tmp_path / "malicioso.zip"
    with zipfile.ZipFile(ruta_zip, "w") as zf:
        zf.writestr("../../../evil.py", "print('pwned')")
    with pytest.raises(RutaMaliciosaError):
        validar_zip(ruta_zip)


def test_validar_zip_rechaza_zip_bomba(tmp_path: Path) -> None:
    ruta_zip = tmp_path / "bomba.zip"
    # Crear archivo con contenido declarado grande (simulado)
    with zipfile.ZipFile(ruta_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Comprimir datos repetitivos que se "expanden"
        contenido = b"A" * 1000
        for i in range(30):
            zf.writestr(f"archivo_{i}.txt", contenido)
    with pytest.raises(ZipBombaError):
        validar_zip(ruta_zip, max_bytes=10_000)  # Límite muy bajo


def test_validar_zip_rechaza_extensiones_no_permitidas(tmp_path: Path) -> None:
    ruta_zip = tmp_path / "con_exe.zip"
    with zipfile.ZipFile(ruta_zip, "w") as zf:
        zf.writestr("virus.exe", "MZ...")
    with pytest.raises(RutaMaliciosaError):
        validar_zip(ruta_zip, extensiones_permitidas=frozenset({".json", ".ttf", ".otf"}))
