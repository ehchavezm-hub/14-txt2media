"""ModoLocalEstricto: bloquea toda red saliente excepto localhost."""

from __future__ import annotations

import threading

_lock = threading.Lock()
_contador: int = 0


class RedBloqueadaError(Exception):
    """Se lanza cuando se intenta acceder a la red en modo local estricto."""


def activar_modo_local() -> None:
    global _contador
    with _lock:
        _contador += 1


def desactivar_modo_local() -> None:
    global _contador
    with _lock:
        if _contador > 0:
            _contador -= 1


def esta_activo() -> bool:
    with _lock:
        return _contador > 0


def verificar_red_permitida(url: str) -> None:
    """Lanza RedBloqueadaError si el modo local está activo y la URL no es localhost."""
    if not esta_activo():
        return
    url_lower = url.lower()
    if "localhost" in url_lower or "127.0.0.1" in url_lower or "::1" in url_lower:
        return
    raise RedBloqueadaError(
        f"Modo local estricto activo: acceso a red bloqueado para {url!r}"
    )


class ModoLocalEstricto:
    """Context manager anidable que activa el modo local estricto."""

    def __enter__(self) -> "ModoLocalEstricto":
        activar_modo_local()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        desactivar_modo_local()
