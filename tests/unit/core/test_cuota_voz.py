"""Tests para el sistema de cuota de voz (thread-safe, JSON persistente)."""

import json
import threading
import time
import pytest
from pathlib import Path

from txt2media.core.cuota_voz import CuotaVoz, CuotaAgotadaError


class TestCuotaVoz:
    def setup_method(self, tmp_path_factory):
        # tmp_path no está disponible en setup_method, se pasa como argumento del test
        pass

    def test_inicializa_con_cero_chars(self, tmp_path):
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=500_000)
        assert cuota.chars_usados_mes() == 0

    def test_registrar_uso_incrementa_contador(self, tmp_path):
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=500_000)
        cuota.registrar_uso(1000)
        assert cuota.chars_usados_mes() == 1000

    def test_multiples_registros_acumulan(self, tmp_path):
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=500_000)
        cuota.registrar_uso(1000)
        cuota.registrar_uso(500)
        assert cuota.chars_usados_mes() == 1500

    def test_exceder_limite_lanza_error(self, tmp_path):
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=500)
        cuota.registrar_uso(400)
        with pytest.raises(CuotaAgotadaError):
            cuota.verificar(200)  # 400+200 > 500

    def test_dentro_del_limite_no_lanza_error(self, tmp_path):
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=500_000)
        cuota.registrar_uso(1000)
        cuota.verificar(1000)  # No debe lanzar

    def test_persiste_en_disco(self, tmp_path):
        ruta = tmp_path / "cuota.json"
        cuota1 = CuotaVoz(ruta=ruta, limite_mensual=500_000)
        cuota1.registrar_uso(2000)
        # Nueva instancia carga del mismo archivo
        cuota2 = CuotaVoz(ruta=ruta, limite_mensual=500_000)
        assert cuota2.chars_usados_mes() == 2000

    def test_archivo_json_bien_formado(self, tmp_path):
        ruta = tmp_path / "cuota.json"
        cuota = CuotaVoz(ruta=ruta, limite_mensual=500_000)
        cuota.registrar_uso(500)
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        assert "chars_usados" in datos
        assert "mes" in datos
        assert datos["chars_usados"] == 500

    def test_reset_en_nuevo_mes(self, tmp_path):
        """Cuando cambia el mes, el contador reinicia."""
        ruta = tmp_path / "cuota.json"
        # Escribir estado del mes pasado
        datos = {
            "mes": "2026-10",
            "chars_usados": 450_000,
        }
        ruta.write_text(json.dumps(datos), encoding="utf-8")
        # Al cargar en nuevo mes (2026-11), debe reiniciar
        cuota = CuotaVoz(ruta=ruta, limite_mensual=500_000, mes_actual="2026-11")
        assert cuota.chars_usados_mes() == 0

    def test_thread_safe_incrementos_concurrentes(self, tmp_path):
        """Múltiples hilos pueden registrar uso sin race conditions."""
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=10_000_000)
        hilos = []
        n_hilos = 20
        chars_por_hilo = 1000

        def registrar():
            cuota.registrar_uso(chars_por_hilo)

        for _ in range(n_hilos):
            t = threading.Thread(target=registrar)
            hilos.append(t)

        for t in hilos:
            t.start()
        for t in hilos:
            t.join()

        assert cuota.chars_usados_mes() == n_hilos * chars_por_hilo

    def test_chars_restantes(self, tmp_path):
        cuota = CuotaVoz(ruta=tmp_path / "cuota.json", limite_mensual=500_000)
        cuota.registrar_uso(100_000)
        assert cuota.chars_restantes() == 400_000
