"""Tests básicos del módulo de motores."""

import pytest


def test_placeholder() -> None:
    """Motor Azure no está disponible en este entorno; test de existencia."""
    pytest.skip("Motor Azure requiere credenciales; se prueba en integración.")
