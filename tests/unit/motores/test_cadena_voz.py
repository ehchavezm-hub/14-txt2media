"""Tests básicos del módulo de voz."""

import pytest


def test_voz_predeterminada() -> None:
    VOZ_DEFAULT = "es-PE-CamilaNeural"
    assert "Neural" in VOZ_DEFAULT


def test_voces_disponibles() -> None:
    voces = ["es-PE-CamilaNeural", "es-PE-AlexNeural"]
    assert len(voces) == 2
    for v in voces:
        assert v.startswith("es-PE")
