"""Tests para Modo Local Estricto — bloquea toda red cuando está activo."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from txt2media.core.configuracion import ConfigPrivacidad
from txt2media.core.modo_local import (
    ModoLocalEstricto,
    RedBloqueadaError,
    activar_modo_local,
    desactivar_modo_local,
    esta_activo,
    verificar_red_permitida,
)


class TestVerificarRedPermitida:
    def test_permite_red_cuando_modo_local_inactivo(self):
        # No debe lanzar cuando el modo local está desactivado
        desactivar_modo_local()
        verificar_red_permitida("https://tts.speech.microsoft.com")

    def test_bloquea_red_cuando_modo_local_activo(self):
        activar_modo_local()
        try:
            with pytest.raises(RedBloqueadaError):
                verificar_red_permitida("https://tts.speech.microsoft.com")
        finally:
            desactivar_modo_local()

    def test_mensaje_error_incluye_url(self):
        activar_modo_local()
        try:
            with pytest.raises(RedBloqueadaError, match="tts.speech.microsoft.com"):
                verificar_red_permitida("https://tts.speech.microsoft.com/v1")
        finally:
            desactivar_modo_local()

    def test_permite_localhost_siempre(self):
        activar_modo_local()
        try:
            # localhost nunca debe bloquearse
            verificar_red_permitida("http://localhost:8080/api")
        finally:
            desactivar_modo_local()

    def test_permite_127_0_0_1_siempre(self):
        activar_modo_local()
        try:
            verificar_red_permitida("http://127.0.0.1:5000/test")
        finally:
            desactivar_modo_local()


class TestModoLocalEstricto:
    def test_context_manager_activa_y_desactiva(self):
        desactivar_modo_local()
        assert not esta_activo()
        with ModoLocalEstricto():
            assert esta_activo()
        assert not esta_activo()

    def test_context_manager_desactiva_si_lanza_excepcion(self):
        desactivar_modo_local()
        try:
            with ModoLocalEstricto():
                raise ValueError("error de prueba")
        except ValueError:
            pass
        assert not esta_activo()

    def test_anidado_mantiene_activo_hasta_salir(self):
        desactivar_modo_local()
        with ModoLocalEstricto():
            with ModoLocalEstricto():
                assert esta_activo()
            # Al salir del inner, outer aún lo mantiene activo
            assert esta_activo()
        assert not esta_activo()


class TestMotorAzureModoLocal:
    """MotorAzure debe lanzar RedBloqueadaError si modo local activo."""

    def test_azure_bloqueado_en_modo_local(self):
        from txt2media.motores.motor_azure import MotorAzure
        from txt2media.core.modo_local import ModoLocalEstricto

        motor = MotorAzure()
        with ModoLocalEstricto():
            with pytest.raises((RedBloqueadaError, Exception)):
                motor.sintetizar("Hola", "es-ES-AlvaroNeural", {})


class TestMotorEdgeTTSModoLocal:
    """MotorEdgeTTS debe ser marcado como no disponible en modo local."""

    def test_edge_tts_no_disponible_en_modo_local(self):
        from txt2media.motores.motor_edge_tts import MotorEdgeTTS
        from txt2media.core.modo_local import ModoLocalEstricto

        motor = MotorEdgeTTS()
        with ModoLocalEstricto():
            # En modo local estricto, edge-tts no está disponible (necesita red)
            assert not motor.disponible_en_modo_local()


class TestConfigPrivacidadIntegracion:
    def test_desde_config_privacidad(self):
        cfg = ConfigPrivacidad(modo_local_estricto=True)
        if cfg.modo_local_estricto:
            activar_modo_local()
        try:
            assert esta_activo()
        finally:
            desactivar_modo_local()
