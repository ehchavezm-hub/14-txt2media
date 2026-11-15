"""Ventana principal de txt2media — PySide6 QMainWindow."""

from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
    from PySide6.QtWidgets import (
        QApplication, QComboBox, QFileDialog, QHBoxLayout,
        QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox,
        QProgressBar, QPushButton, QStatusBar, QVBoxLayout, QWidget,
        QGroupBox, QFormLayout,
    )
    _PYSIDE6_OK = True
except ImportError:
    _PYSIDE6_OK = False


class VentanaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("txt2media v1.0.1")
        self.setMinimumSize(QSize(720, 540))
        self.setAcceptDrops(True)
        self._worker = None
        self._archivos: list[Path] = []
        self._init_ui()
        self._aplicar_tema()

    # ------------------------------------------------------------------ #
    def _init_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Área de archivos
        grp_archivos = QGroupBox("Archivos de entrada")
        v_arch = QVBoxLayout(grp_archivos)
        self.lista_archivos = QListWidget()
        self.lista_archivos.setMinimumHeight(120)
        btn_row = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar archivos…")
        self.btn_quitar = QPushButton("Quitar selección")
        btn_row.addWidget(self.btn_agregar)
        btn_row.addWidget(self.btn_quitar)
        btn_row.addStretch()
        v_arch.addWidget(QLabel("Arrastra archivos EPUB/PDF/DOCX/MD aquí o usa el botón:"))
        v_arch.addWidget(self.lista_archivos)
        v_arch.addLayout(btn_row)
        layout.addWidget(grp_archivos)

        # Opciones
        grp_opc = QGroupBox("Opciones de conversión")
        form = QFormLayout(grp_opc)

        self.combo_formato = QComboBox()
        for fmt in ("pptx", "docx", "xlsx", "audio", "video"):
            self.combo_formato.addItem(fmt.upper(), fmt)
        form.addRow("Formato de salida:", self.combo_formato)

        self.combo_modo = QComboBox()
        self.combo_modo.addItem("Completo (un archivo)", "completo")
        self.combo_modo.addItem("Por capítulos (BookPlayer)", "capitulos")
        form.addRow("Modo audio:", self.combo_modo)

        self.combo_voz = QComboBox()
        self.combo_voz.addItem("Camila (es-PE-CamilaNeural)", "es-PE-CamilaNeural")
        self.combo_voz.addItem("Alex (es-PE-AlexNeural)", "es-PE-AlexNeural")
        form.addRow("Voz TTS:", self.combo_voz)

        self.edit_salida = QLineEdit(".")
        btn_carpeta = QPushButton("…")
        btn_carpeta.setMaximumWidth(32)
        h_sal = QHBoxLayout()
        h_sal.addWidget(self.edit_salida)
        h_sal.addWidget(btn_carpeta)
        form.addRow("Carpeta de salida:", h_sal)

        layout.addWidget(grp_opc)

        # Barra progreso
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)
        layout.addWidget(self.barra_progreso)

        # Botones acción
        h_btn = QHBoxLayout()
        self.btn_convertir = QPushButton("Convertir")
        self.btn_convertir.setMinimumHeight(40)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setEnabled(False)
        h_btn.addWidget(self.btn_convertir)
        h_btn.addWidget(self.btn_cancelar)
        layout.addLayout(h_btn)

        # Barra de estado
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Listo")

        # Conexiones
        self.btn_agregar.clicked.connect(self._agregar_archivos)
        self.btn_quitar.clicked.connect(self._quitar_archivo)
        btn_carpeta.clicked.connect(self._seleccionar_carpeta)
        self.btn_convertir.clicked.connect(self._iniciar_conversion)
        self.btn_cancelar.clicked.connect(self._cancelar_conversion)
        self.combo_formato.currentIndexChanged.connect(self._on_formato_cambiado)
        self._on_formato_cambiado()

    def _aplicar_tema(self) -> None:
        from txt2media.core.tema import TEMA
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: #FAFAFA; }}
            QGroupBox {{ font-weight: bold; border: 1px solid #CCCCCC; border-radius: 4px;
                         margin-top: 8px; padding-top: 8px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 8px; color: {TEMA.azul}; }}
            QPushButton {{ background-color: {TEMA.azul}; color: white; border-radius: 4px;
                           padding: 6px 14px; }}
            QPushButton:hover {{ background-color: {TEMA.azul_claro}; }}
            QPushButton:disabled {{ background-color: #AAAAAA; }}
            QProgressBar {{ border: 1px solid #CCCCCC; border-radius: 4px; text-align: center; }}
            QProgressBar::chunk {{ background-color: {TEMA.naranja}; }}
        """)

    # ------------------------------------------------------------------ #
    def dragEnterEvent(self, event: "QDragEnterEvent") -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: "QDropEvent") -> None:
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in (".epub", ".pdf", ".docx", ".md"):
                self._agregar_path(path)
        event.acceptProposedAction()

    # ------------------------------------------------------------------ #
    def _agregar_archivos(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos",
            "",
            "Documentos (*.epub *.pdf *.docx *.md);;Todos (*)",
        )
        for p in paths:
            self._agregar_path(Path(p))

    def _agregar_path(self, path: Path) -> None:
        if path not in self._archivos:
            self._archivos.append(path)
            self.lista_archivos.addItem(str(path))

    def _quitar_archivo(self) -> None:
        row = self.lista_archivos.currentRow()
        if row >= 0:
            self.lista_archivos.takeItem(row)
            self._archivos.pop(row)

    def _seleccionar_carpeta(self) -> None:
        carpeta = QFileDialog.getExistingDirectory(self, "Carpeta de salida")
        if carpeta:
            self.edit_salida.setText(carpeta)

    def _on_formato_cambiado(self) -> None:
        fmt = self.combo_formato.currentData()
        es_audio = fmt == "audio"
        self.combo_modo.setEnabled(es_audio)
        self.combo_voz.setEnabled(fmt in ("audio", "video"))

    # ------------------------------------------------------------------ #
    def _iniciar_conversion(self) -> None:
        if not self._archivos:
            QMessageBox.warning(self, "Sin archivos", "Agrega al menos un archivo.")
            return

        from txt2media.ui.worker_conversion import WorkerConversion

        fmt = self.combo_formato.currentData()
        modo = self.combo_modo.currentData()
        voz = self.combo_voz.currentData()
        carpeta = Path(self.edit_salida.text() or ".")

        self._worker = WorkerConversion(
            archivos=self._archivos,
            formato=fmt,
            carpeta_salida=carpeta,
            voz=voz,
            modo=modo,
        )
        self._worker.progreso.connect(self._on_progreso)
        self._worker.completado.connect(self._on_completado)
        self._worker.error.connect(self._on_error)

        self.btn_convertir.setEnabled(False)
        self.btn_cancelar.setEnabled(True)
        self.barra_progreso.setValue(0)
        self._worker.start()

    def _cancelar_conversion(self) -> None:
        if self._worker:
            self._worker.cancelar()
        self.status.showMessage("Cancelando…")

    def _on_progreso(self, actual: int, total: int, nombre: str) -> None:
        pct = int(actual / total * 100) if total else 0
        self.barra_progreso.setValue(pct)
        self.status.showMessage(f"[{actual}/{total}] {nombre}")

    def _on_completado(self, resultados: list) -> None:
        self.barra_progreso.setValue(100)
        self.btn_convertir.setEnabled(True)
        self.btn_cancelar.setEnabled(False)
        n = len(resultados)
        self.status.showMessage(f"Completado: {n} archivo(s) generado(s)")
        QMessageBox.information(
            self, "Completado", f"Se generaron {n} archivo(s).\n{self.edit_salida.text()}"
        )

    def _on_error(self, mensaje: str) -> None:
        self.status.showMessage(f"Error: {mensaje}")
        QMessageBox.critical(self, "Error", mensaje)
        self.btn_convertir.setEnabled(True)
        self.btn_cancelar.setEnabled(False)


def lanzar_app() -> None:
    if not _PYSIDE6_OK:
        print("PySide6 no instalado. Usa: pip install PySide6>=6.10.0")
        return
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
