"""Tests para los motores de voz y la CadenaVoz (fallback chain)."""

import pytest
from unittest.mock import patch, MagicMock

from txt2media.core.base_voz import ErrorVoz, ClaveInvalidaError, CuotaAgotadaError
from txt2media.core.modelo import NivelResumen
from txt2media.motores.cadena_voz import CadenaVoz
from txt2media.motores.motor_sapi import MotorSAPI


class _MotorSimulado:
    """Motor stub para tests."""
    def __init__(self, nombre, disponible=True, resultado=b"audio", lanza=None):
        self._nombre = nombre
        self._disponible = disponible
        self._resultado = resultado
        self._lanza = lanza
        self.llamadas = 0

    @property
    def nombre(self):
        return self._nombre

    def disponible(self):
        return self._disponible

    def sintetizar(self, texto, voz, config):
        self.llamadas += 1
        if self._lanza:
            raise self._lanza
        return self._resultado


class TestCadenaVoz:
    def test_usa_primer_motor_disponible(self):
        m1 = _MotorSimulado("azure", disponible=True, resultado=b"azure_audio")
        m2 = _MotorSimulado("edge", disponible=True, resultado=b"edge_audio")
        cadena = CadenaVoz(motores=[m1, m2])
        resultado = cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})
        assert resultado == b"azure_audio"
        assert m1.llamadas == 1
        assert m2.llamadas == 0

    def test_cae_al_siguiente_si_falla(self):
        m1 = _MotorSimulado("azure", lanza=ErrorVoz("fallo azure"))
        m2 = _MotorSimulado("edge", resultado=b"edge_audio")
        cadena = CadenaVoz(motores=[m1, m2])
        resultado = cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})
        assert resultado == b"edge_audio"
        assert m2.llamadas == 1

    def test_cae_hasta_sapi_si_los_demas_fallan(self):
        m1 = _MotorSimulado("azure", lanza=ClaveInvalidaError("401"))
        m2 = _MotorSimulado("edge", lanza=ErrorVoz("edge fallo"))
        m3 = _MotorSimulado("sapi", resultado=b"sapi_audio")
        cadena = CadenaVoz(motores=[m1, m2, m3])
        resultado = cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})
        assert resultado == b"sapi_audio"

    def test_lanza_error_si_todos_fallan(self):
        m1 = _MotorSimulado("azure", lanza=ErrorVoz("fallo 1"))
        m2 = _MotorSimulado("edge", lanza=ErrorVoz("fallo 2"))
        cadena = CadenaVoz(motores=[m1, m2])
        with pytest.raises(ErrorVoz):
            cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})

    def test_salta_motores_no_disponibles(self):
        m1 = _MotorSimulado("azure", disponible=False)
        m2 = _MotorSimulado("edge", disponible=True, resultado=b"edge_audio")
        cadena = CadenaVoz(motores=[m1, m2])
        resultado = cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})
        assert resultado == b"edge_audio"
        assert m1.llamadas == 0

    def test_clave_invalida_no_vuelve_a_azure(self):
        """Un 401 no debe reintentar Azure, debe pasar al siguiente."""
        m1 = _MotorSimulado("azure", lanza=ClaveInvalidaError("401"))
        m2 = _MotorSimulado("edge", resultado=b"edge_audio")
        cadena = CadenaVoz(motores=[m1, m2])
        cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})
        # Azure solo se llamó una vez, no reintentó
        assert m1.llamadas == 1

    def test_cadena_sin_motores_lanza_error(self):
        cadena = CadenaVoz(motores=[])
        with pytest.raises(ErrorVoz):
            cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})

    def test_motor_seleccionado_reportado(self):
        m1 = _MotorSimulado("azure", lanza=ErrorVoz("fallo"))
        m2 = _MotorSimulado("edge", resultado=b"edge_audio")
        cadena = CadenaVoz(motores=[m1, m2])
        cadena.sintetizar("Hola", "es-ES-AlvaroNeural", {})
        assert cadena.ultimo_motor_usado == "edge"


class TestMotorSAPIDisponibilidad:
    """SAPI solo está disponible en Windows; en Linux debe devolver False."""

    def test_sapi_no_disponible_en_linux(self):
        motor = MotorSAPI()
        import sys
        if sys.platform != "win32":
            assert motor.disponible() is False

    def test_sapi_nombre(self):
        motor = MotorSAPI()
        assert motor.nombre == "sapi"

    def test_sapi_sintetizar_en_linux_lanza_error(self):
        import sys
        if sys.platform != "win32":
            motor = MotorSAPI()
            with pytest.raises(ErrorVoz):
                motor.sintetizar("Hola", "es", {})
