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


@pytest.fixture
def ventana(app):
    from PySide6.QtCore import QSettings
    QSettings("txt2media", "txt2media").clear()
    from txt2media.ui.ventana_principal import VentanaPrincipal
    v = VentanaPrincipal()
    yield v
    v.close()


@skip_sin_qt
class TestVentanaPrincipal:
    def test_ventana_crea_sin_error(self, ventana):
        assert ventana is not None

    def test_ventana_tiene_titulo(self, ventana):
        assert "txt2media" in ventana.windowTitle()

    def test_controles_principales_existen(self, ventana):
        for nombre in ("btn_agregar", "btn_quitar", "btn_convertir", "btn_cancelar",
                       "btn_abrir_carpeta", "barra_progreso", "lista_archivos", "edit_salida"):
            assert getattr(ventana, nombre) is not None, nombre

    def test_cancelar_deshabilitado_sin_proceso(self, ventana):
        assert not ventana.btn_cancelar.isEnabled()

    def test_siete_formatos_disponibles(self, ventana):
        datos = {ventana.combo_formato._datos[i] for i in range(ventana.combo_formato.count())}
        assert datos == {"pptx", "docx", "xlsx", "md", "html", "audio", "video"}

    def test_voz_predeterminada_camila(self, ventana):
        assert ventana.combo_voz.currentData() == "es-PE-CamilaNeural"

    def test_opciones_de_voz_solo_para_audio_y_video(self, ventana):
        sel = ventana.combo_formato
        sel.setCurrentIndex(sel.findData("pptx"))
        assert ventana.bloque_voz.isHidden()
        sel.setCurrentIndex(sel.findData("video"))
        assert not ventana.bloque_voz.isHidden()
        assert ventana.combo_modo.isHidden()
        sel.setCurrentIndex(sel.findData("audio"))
        assert not ventana.combo_modo.isHidden()

    def test_agregar_y_quitar_archivo(self, ventana, tmp_path):
        doc = tmp_path / "libro.pdf"
        doc.write_bytes(b"x" * 2048)
        ventana._agregar_path(doc)
        ventana._agregar_path(doc)  # duplicado ignorado
        assert ventana._archivos == [doc]
        assert ventana.lista_archivos.count() == 1
        assert ventana.pila_entrada.currentIndex() == 1
        ventana._quitar_ruta(doc)
        assert ventana._archivos == []
        assert ventana.lista_archivos.count() == 0
        assert ventana.pila_entrada.currentIndex() == 0


@skip_sin_qt
class TestWorkerConversion:
    def test_worker_crea_sin_error(self, app, tmp_path):
        from txt2media.ui.worker_conversion import WorkerConversion
        worker = WorkerConversion(archivos=[], formato="pptx", carpeta_salida=tmp_path)
        assert worker is not None

    def test_worker_es_qthread(self, app, tmp_path):
        from PySide6.QtCore import QThread
        from txt2media.ui.worker_conversion import WorkerConversion
        worker = WorkerConversion(archivos=[], formato="pptx", carpeta_salida=tmp_path)
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
