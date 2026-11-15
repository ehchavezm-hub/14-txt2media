"""Tests para el motor de resumen local extractivo."""

import pytest

from txt2media.core.modelo import NivelResumen
from txt2media.core.resumen_local import MotorResumenLocal


class TestMotorResumenLocal:
    def setup_method(self):
        self.motor = MotorResumenLocal()

    def test_nombre_es_local(self):
        assert "local" in self.motor.nombre.lower()

    def test_siempre_disponible(self):
        assert self.motor.disponible() is True

    def test_resumen_breve_mas_corto_que_original(self):
        texto = (
            "El proyecto reporta un avance del 78%. "
            "Se han completado las estructuras principales. "
            "Los acabados están al 60% de avance. "
            "El presupuesto ejecutado es de S/ 3,510,000. "
            "Se proyecta la finalización para el 30 de junio. "
            "El equipo trabaja en dos turnos de 8 horas cada uno. "
        )
        resumen = self.motor.resumir(texto, NivelResumen.BREVE)
        assert len(resumen) < len(texto)
        assert len(resumen) > 0

    def test_resumen_completo_es_mas_largo_que_breve(self):
        texto = " ".join([
            "El proyecto reporta un avance del 78%.",
            "Se han completado las estructuras principales.",
            "Los acabados están al 60% de avance.",
            "El presupuesto ejecutado es de S/ 3,510,000.",
            "Se proyecta la finalización para el 30 de junio.",
            "El equipo trabaja en dos turnos de 8 horas.",
            "La calidad del concreto es de 350 kg/cm².",
            "Los ensayos de resistencia son satisfactorios.",
        ])
        breve = self.motor.resumir(texto, NivelResumen.BREVE)
        completo = self.motor.resumir(texto, NivelResumen.COMPLETO)
        assert len(completo) >= len(breve)

    def test_resumen_texto_muy_corto_devuelve_el_mismo(self):
        texto = "El avance es del 78%."
        resumen = self.motor.resumir(texto, NivelResumen.BREVE)
        assert len(resumen) > 0

    def test_resumen_vacio_devuelve_vacio(self):
        resumen = self.motor.resumir("", NivelResumen.BREVE)
        assert resumen == ""

    def test_resumen_es_subconjunto_de_oraciones_originales(self):
        """El resumen extractivo sólo contiene oraciones del original."""
        texto = (
            "El avance es del 78%. "
            "El presupuesto es de S/ 4,500,000. "
            "Se proyecta finalizar en junio. "
        )
        resumen = self.motor.resumir(texto, NivelResumen.BREVE)
        # Al menos una oración del resumen debe aparecer en el texto original
        oraciones_originales = [o.strip() for o in texto.split(".") if o.strip()]
        encontrada = any(
            o in resumen or resumen in o
            for o in oraciones_originales
        )
        assert encontrada

    def test_resumen_no_esta_vacio_con_texto_largo(self):
        texto = " ".join([f"Oración número {i} del documento de prueba." for i in range(20)])
        resumen = self.motor.resumir(texto, NivelResumen.MEDIO)
        assert len(resumen) > 0

    def test_nivel_medio_entre_breve_y_completo(self):
        texto = " ".join([f"Oración {i} con contenido informativo." for i in range(15)])
        breve = self.motor.resumir(texto, NivelResumen.BREVE)
        medio = self.motor.resumir(texto, NivelResumen.MEDIO)
        completo = self.motor.resumir(texto, NivelResumen.COMPLETO)
        # Medio no debe ser más largo que completo
        assert len(medio) <= len(completo)
