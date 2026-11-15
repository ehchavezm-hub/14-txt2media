"""Clases base e interfaces para motores de voz."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ErrorVoz(Exception):
    """Error genérico de motor de voz."""


class ClaveInvalidaError(ErrorVoz):
    """La clave de API es inválida o no está configurada."""


class CuotaAgotadaError(ErrorVoz):
    """Se ha agotado la cuota mensual del servicio."""


class MotorVoz(ABC):
    """Interfaz base para motores de síntesis de voz."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre identificador del motor."""

    @abstractmethod
    def disponible(self) -> bool:
        """True si el motor puede usarse en el entorno actual."""

    @abstractmethod
    def sintetizar(self, texto: str, voz: str, config: dict) -> bytes:
        """Sintetiza texto y devuelve bytes de audio (WAV o MP3)."""

    def disponible_en_modo_local(self) -> bool:
        """True si el motor funciona sin red."""
        return False
