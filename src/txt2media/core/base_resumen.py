"""Interfaz abstracta para los motores de resumen."""

from abc import ABC, abstractmethod

from txt2media.core.modelo import NivelResumen


class MotorDesactivadoError(RuntimeError):
    """El motor de resumen no está configurado o está desactivado."""


class MotorResumen(ABC):
    """Contrato para motores de resumen de texto."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre identificador del motor (ej: 'local', 'claude')."""

    @abstractmethod
    def resumir(self, texto: str, nivel: NivelResumen) -> str:
        """Resume el texto al nivel indicado.

        Returns:
            Texto resumido; nunca más largo que el original para niveles BREVE y MEDIO.
            Para COMPLETO devuelve el texto íntegro.

        Lanza:
            MotorDesactivadoError: si el motor no está disponible.
        """

    def disponible(self) -> bool:
        """Devuelve True si el motor está configurado y listo para usar."""
        return True
