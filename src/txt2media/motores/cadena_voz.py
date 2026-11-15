"""CadenaVoz: Azure → edge-tts → SAPI con fallback automático."""

from __future__ import annotations

import logging
from pathlib import Path

from txt2media.core.base_voz import ErrorVoz, MotorVoz
from txt2media.core.modo_local import esta_activo

_log = logging.getLogger("txt2media.cadena_voz")


class CadenaVoz:
    def __init__(self, voz: str = "es-PE-CamilaNeural") -> None:
        self._voz = voz
        self._motores: list[MotorVoz] = _construir_cadena()

    @property
    def voz(self) -> str:
        return self._voz

    @voz.setter
    def voz(self, nueva_voz: str) -> None:
        self._voz = nueva_voz

    def sintetizar(self, texto: str, salida: Path) -> str:
        """Sintetiza texto y devuelve el nombre del motor usado."""
        modo_local = esta_activo()
        ultimo_error: Exception | None = None

        for motor in self._motores:
            if modo_local and not motor.disponible_en_modo_local():
                _log.debug("Motor %s omitido (modo local)", motor.nombre)
                continue
            if not motor.disponible():
                _log.debug("Motor %s no disponible", motor.nombre)
                continue
            try:
                motor.sintetizar(texto, self._voz, salida)
                _log.info("Audio generado con motor: %s", motor.nombre)
                return motor.nombre
            except ErrorVoz as exc:
                _log.warning("Motor %s falló: %s", motor.nombre, exc)
                ultimo_error = exc

        raise ErrorVoz(
            f"Todos los motores fallaron. Último error: {ultimo_error}"
        )

    def motor_disponible(self) -> str | None:
        """Devuelve el nombre del primer motor disponible."""
        modo_local = esta_activo()
        for motor in self._motores:
            if modo_local and not motor.disponible_en_modo_local():
                continue
            if motor.disponible():
                return motor.nombre
        return None


def _construir_cadena() -> list[MotorVoz]:
    from txt2media.motores.motor_azure import MotorAzure
    from txt2media.motores.motor_edge_tts import MotorEdgeTTS
    from txt2media.motores.motor_sapi import MotorSAPI

    return [MotorAzure(), MotorEdgeTTS(), MotorSAPI()]
