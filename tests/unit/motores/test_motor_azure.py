"""Tests para MotorAzure — fragmentación, SSML, manejo de HTTP."""

import pytest

from txt2media.motores.motor_azure import _fragmentar, _ssml


class TestFragmentar:
    def test_texto_corto_no_se_fragmenta(self):
        texto = "Hola mundo."
        frags = _fragmentar(texto, max_chars=3000)
        assert frags == [texto]

    def test_texto_largo_se_divide(self):
        texto = " ".join([f"Oración {i}." for i in range(200)])
        frags = _fragmentar(texto, max_chars=500)
        assert len(frags) > 1
        assert all(len(f) <= 500 for f in frags)

    def test_fragmentos_cubren_todo_el_texto(self):
        texto = " ".join([f"Frase {i}." for i in range(50)])
        frags = _fragmentar(texto, max_chars=200)
        reconstruido = " ".join(frags)
        # Todas las palabras originales están en algún fragmento
        for frase in [f"Frase {i}." for i in range(50)]:
            assert frase in reconstruido

    def test_max_chars_se_respeta(self):
        texto = "A " * 2000  # 4000 chars aprox
        frags = _fragmentar(texto, max_chars=1000)
        assert all(len(f) <= 1000 for f in frags)


class TestSSML:
    def test_ssml_contiene_voz(self):
        ssml = _ssml("Hola", "es-ES-AlvaroNeural")
        assert "es-ES-AlvaroNeural" in ssml

    def test_ssml_contiene_texto(self):
        ssml = _ssml("Texto de prueba", "es-ES-AlvaroNeural")
        assert "Texto de prueba" in ssml

    def test_ssml_escapa_ampersand(self):
        ssml = _ssml("A&B", "es-ES-AlvaroNeural")
        assert "&amp;" in ssml
        assert "A&B" not in ssml

    def test_ssml_escapa_menor_que(self):
        ssml = _ssml("x < y", "es-ES-AlvaroNeural")
        assert "&lt;" in ssml

    def test_ssml_es_xml_bien_formado(self):
        import xml.etree.ElementTree as ET
        ssml = _ssml("Texto simple.", "es-ES-AlvaroNeural")
        ET.fromstring(ssml)  # No debe lanzar
