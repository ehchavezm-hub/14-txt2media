"""Tests del modo local estricto."""
import pytest
from txt2media.core.modo_local import (
    ModoLocalEstricto,
    RedBloqueadaError,
    activar_modo_local,
    desactivar_modo_local,
    esta_activo,
    verificar_red_permitida,
)


def test_modo_local_inactivo_por_defecto():
    desactivar_modo_local()
    assert not esta_activo()


def test_activar_desactivar():
    activar_modo_local()
    assert esta_activo()
    desactivar_modo_local()
    assert not esta_activo()


def test_context_manager():
    with ModoLocalEstricto():
        assert esta_activo()
    assert not esta_activo()


def test_context_manager_anidado():
    with ModoLocalEstricto():
        with ModoLocalEstricto():
            assert esta_activo()
        assert esta_activo()
    assert not esta_activo()


def test_verificar_red_bloqueada():
    with ModoLocalEstricto():
        with pytest.raises(RedBloqueadaError):
            verificar_red_permitida("api.example.com")


def test_localhost_permitido_en_modo_local():
    with ModoLocalEstricto():
        verificar_red_permitida("localhost")
        verificar_red_permitida("127.0.0.1")
