"""Clase base abstracta para todos los lectores de documentos."""

from abc import ABC, abstractmethod
from pathlib import Path

from txt2media.core.modelo import Documento


class BaseLector(ABC):
    """Contrato que todo lector debe cumplir.

    Los lectores solo producen `Documento`; no conocen los formatos de salida.
    """

    @property
    @abstractmethod
    def formatos_soportados(self) -> list[str]:
        """Lista de extensiones que maneja este lector (ej: ['.pdf', '.PDF'])."""

    @abstractmethod
    def leer(self, ruta: Path) -> Documento:
        """Lee el documento en la ruta dada y devuelve un `Documento`.

        Lanza:
            FileNotFoundError: si la ruta no existe.
            ValueError: si el archivo está corrupto o protegido.
            IsADirectoryError: si la ruta es un directorio.
        """

    def puede_leer(self, ruta: Path) -> bool:
        """Devuelve True si este lector soporta el archivo dado."""
        return ruta.suffix.lower() in [f.lower() for f in self.formatos_soportados]
