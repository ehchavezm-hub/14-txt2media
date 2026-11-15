"""Clase base abstracta para todos los generadores de salida."""

from abc import ABC, abstractmethod
from pathlib import Path

from txt2media.core.modelo import Documento


class BaseGenerador(ABC):
    """Contrato que todo generador debe cumplir.

    Los generadores solo consumen `Documento`; no conocen el formato de origen.
    """

    @property
    @abstractmethod
    def formato(self) -> str:
        """Identificador del formato de salida (ej: 'docx', 'pptx', 'mp3')."""

    @abstractmethod
    def generar(self, doc: Documento, destino: Path, config: dict[str, object]) -> Path:
        """Genera el archivo de salida y lo escribe en `destino`.

        Usa escritura atómica: el archivo de destino solo existe completo o no existe.

        Args:
            doc: El documento a convertir.
            destino: Directorio donde se escribirá el archivo de salida.
            config: Configuración específica del generador.

        Returns:
            Ruta completa al archivo generado.

        Lanza:
            ValueError: si el documento está vacío o es inválido para este formato.
            OSError: si no se puede escribir en el destino.
        """
