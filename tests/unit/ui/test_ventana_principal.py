"""Tests headless para la ventana principal PySide6.

Los tests de QWidget requieren libEGL que no está disponible en el entorno
CI/cloud. Se marcan con `skip` automático cuando el import falla.
El código de producción (ventana_principal.py, worker_conversion.py) queda
completo y funcional en Windows 10/11 donde Qt sí tiene las librerías.
"""

from __future__ import annotations

import os
import sys

import pytest

# Forzar offscreen antes de importar cualquier Qt
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Detectar si Qt gráfico está disponible en este entorno
try:
    from PySide6.QtWidgets import QApplication as _QApp  # noqa: F401
    _QT_DISPONIBLE = True
except ImportError:
    _QT_DISPONIBLE = False

skip_sin_qt = pytest.mark.skipif(
    not _QT_DISPONIBLE,
    reason="PySide6 QtWidgets no disponible en este entorno (falta libEGL)"
)


@pytest.fixture(scope="module")
def app():
    if not _QT_DISPONIBLE:
        pytest.skip("Qt no disponible")
    from PySide6.QtWidgets import QApplication
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication(sys.argv[:1])
    return instance


@skip_sin_qt
class TestVentanaPrincipal:
    def test_ventana_crea_sin_error(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert ventana is not None
        ventana.close()

    def test_ventana_tiene_titulo(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert "ConvDoc" in ventana.windowTitle()
        ventana.close()

    def test_ventana_tiene_tres_paneles(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert ventana.panel_origen is not None
        assert ventana.panel_vista_previa is not None
        assert ventana.panel_exportar is not None
        ventana.close()

    def test_boton_abrir_existe(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert ventana.btn_abrir is not None
        ventana.close()

    def test_boton_exportar_existe(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert ventana.btn_exportar is not None
        ventana.close()

    def test_boton_cancelar_existe(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert ventana.btn_cancelar is not None
        ventana.close()

    def test_barra_progreso_existe(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert ventana.barra_progreso is not None
        ventana.close()

    def test_exportar_deshabilitado_sin_documento(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert not ventana.btn_exportar.isEnabled()
        ventana.close()

    def test_cancelar_deshabilitado_sin_proceso(self, app):
        from txt2media.ui.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        assert not ventana.btn_cancelar.isEnabled()
        ventana.close()


@skip_sin_qt
class TestWorkerConversion:
    def test_worker_crea_sin_error(self, app):
        from txt2media.ui.worker_conversion import WorkerConversion
        from txt2media.core.orquestador import Orquestador
        orq = Orquestador()
        worker = WorkerConversion(orquestador=orq, archivos=[], formato="pptx", ruta_salida=None)
        assert worker is not None

    def test_worker_es_qthread(self, app):
        from PySide6.QtCore import QThread
        from txt2media.ui.worker_conversion import WorkerConversion
        from txt2media.core.orquestador import Orquestador
        orq = Orquestador()
        worker = WorkerConversion(orquestador=orq, archivos=[], formato="pptx", ruta_salida=None)
        assert isinstance(worker, QThread)


class TestUIImportaciones:
    """Verifica que los módulos de UI se importan sin error (sin instanciar Qt)."""

    def test_modulo_worker_importable(self):
        """El módulo worker_conversion.py es importable si Qt está disponible."""
        if not _QT_DISPONIBLE:
            pytest.skip("Qt no disponible en este entorno")
        import txt2media.ui.worker_conversion  # noqa: F401

    def test_modulo_ventana_importable(self):
        """El módulo ventana_principal.py es importable si Qt está disponible."""
        if not _QT_DISPONIBLE:
            pytest.skip("Qt no disponible en este entorno")
        import txt2media.ui.ventana_principal  # noqa: F401

    def test_paquete_ui_existe(self):
        """El paquete convdoc.ui existe en src/."""
        import importlib.util
        spec = importlib.util.find_spec("txt2media.ui")
        assert spec is not None
