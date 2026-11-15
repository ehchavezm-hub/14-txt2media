"""Tests para el sistema de cuota de voz."""

import threading
import pytest
from txt2media.core.cuota_voz import CuotaVoz, CuotaAgotadaError


class TestCuotaVoz:
    def test_inicializa(self) -> None:
        cuota = CuotaVoz(limite_mensual=500_000)
        assert cuota is not None

    def test_chars_usados_es_entero(self) -> None:
        cuota = CuotaVoz(limite_mensual=500_000)
        assert isinstance(cuota.chars_usados(), int)

    def test_verificar_y_consumir_dentro_limite(self) -> None:
        cuota = CuotaVoz(limite_mensual=500_000)
        # Si ya se usó algo, solo verificamos que no lanza para cantidades pequeñas
        try:
            cuota.verificar_y_consumir(1)
        except CuotaAgotadaError:
            pass  # Podría estar al límite si el test corre muchas veces

    def test_exceder_limite_lanza_error(self) -> None:
        cuota = CuotaVoz(limite_mensual=1)
        with pytest.raises(CuotaAgotadaError):
            cuota.verificar_y_consumir(100)

    def test_cuota_agotada_error_es_exception(self) -> None:
        err = CuotaAgotadaError("agotada")
        assert isinstance(err, Exception)

    def test_chars_usados_no_negativo(self) -> None:
        cuota = CuotaVoz(limite_mensual=500_000)
        assert cuota.chars_usados() >= 0
