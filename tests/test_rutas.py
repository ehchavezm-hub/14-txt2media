"""Tests de get_datos_dir."""
import os
from pathlib import Path


def test_modo_dev(monkeypatch, tmp_path):
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)
    from importlib import reload
    import txt2media.utils.rutas as rutas
    reload(rutas)
    resultado = rutas.get_datos_dir()
    assert resultado == Path("datos_dev")


def test_modo_produccion_no_dev(monkeypatch):
    monkeypatch.delenv("CONVDOC_DEV", raising=False)
    from importlib import reload
    import txt2media.utils.rutas as rutas
    reload(rutas)
    resultado = rutas.get_datos_dir()
    assert isinstance(resultado, Path)
    assert "txt2media" in str(resultado)
