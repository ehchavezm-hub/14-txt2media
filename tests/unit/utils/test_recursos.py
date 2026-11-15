"""Tests para utils.rutas y utils.seguridad."""

import zipfile
from pathlib import Path

import pytest

from txt2media.utils.rutas import get_datos_dir
from txt2media.utils.seguridad import RutaMaliciosaError, ZipBombaError, validar_zip


def test_get_datos_dir_devuelve_path() -> None:
    ruta = get_datos_dir()
    assert isinstance(ruta, Path)


def test_ruta_maliciosa_error_es_exception() -> None:
    err = RutaMaliciosaError("ruta maliciosa")
    assert isinstance(err, Exception)


def test_zip_bomba_error_es_exception() -> None:
    err = ZipBombaError("zip bomba")
    assert isinstance(err, Exception)


def test_validar_zip_archivo_normal(tmp_path) -> None:
    ruta = tmp_path / "normal.zip"
    with zipfile.ZipFile(str(ruta), "w") as zf:
        zf.writestr("file.txt", "contenido normal")
    validar_zip(ruta)  # no debe lanzar


def test_validar_zip_path_traversal(tmp_path) -> None:
    ruta = tmp_path / "malicioso.zip"
    with zipfile.ZipFile(str(ruta), "w") as zf:
        zf.writestr("../../../etc/passwd", "root:x:0:0")
    with pytest.raises((RutaMaliciosaError, Exception)):
        validar_zip(ruta)
