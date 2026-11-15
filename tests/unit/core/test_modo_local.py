"""Tests para ModoLocalEstricto."""

from txt2media.core.modo_local import (
    ModoLocalEstricto, RedBloqueadaError,
    activar_modo_local, desactivar_modo_local, esta_activo,
)


def test_inicialmente_inactivo() -> None:
    desactivar_modo_local()
    desactivar_modo_local()
    assert not esta_activo()


def test_activar_modo_local() -> None:
    activar_modo_local()
    assert esta_activo()
    desactivar_modo_local()


def test_modo_local_context_manager() -> None:
    with ModoLocalEstricto():
        assert esta_activo()
    assert not esta_activo()


def test_error_bloqueada_es_exception() -> None:
    err = RedBloqueadaError("red bloqueada")
    assert isinstance(err, Exception)
