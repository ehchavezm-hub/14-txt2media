"""Ventana principal txt2media — diseño profesional PySide6."""

from __future__ import annotations
from pathlib import Path

try:
    from PySide6.QtCore import Qt, QSize, QThread, QTimer
    from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QFont, QColor, QPalette
    from PySide6.QtWidgets import (
        QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel,
        QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
        QProgressBar, QPushButton, QSizePolicy, QStatusBar, QVBoxLayout,
        QWidget, QFrame, QFormLayout, QGroupBox, QSpacerItem,
    )
    _PYSIDE6_OK = True
except ImportError:
    _PYSIDE6_OK = False

_EXT_ICONOS = {
    ".pdf": "📄", ".epub": "📚", ".docx": "📝", ".md": "📋",
}

_QSS = """
/* ── Base ── */
QMainWindow, QWidget#central {
    background: #1C1C2E;
    color: #E8E8F0;
}

/* ── Header ── */
QWidget#header {
    background: #12122A;
    border-bottom: 2px solid #4E79A7;
}
QLabel#app_titulo {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#app_version {
    color: #4E79A7;
    font-size: 11px;
}

/* ── Panel izquierdo ── */
QWidget#panel_izq {
    background: #16162A;
    border-right: 1px solid #2A2A45;
}
QLabel#sec_label {
    color: #7A7A9A;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Lista de archivos ── */
QListWidget {
    background: #0E0E20;
    border: 1px solid #2A2A45;
    border-radius: 6px;
    color: #C8C8E0;
    font-size: 12px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 4px;
    border-bottom: 1px solid #1A1A32;
}
QListWidget::item:hover    { background: #252545; }
QListWidget::item:selected { background: #2D3A6A; color: #FFFFFF; border-left: 3px solid #4E79A7; }

/* ── ComboBox ── */
QComboBox {
    background: #0E0E20;
    border: 1px solid #2A2A45;
    border-radius: 5px;
    color: #C8C8E0;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 28px;
}
QComboBox:hover   { border-color: #4E79A7; }
QComboBox:focus   { border-color: #4E79A7; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #16162A;
    border: 1px solid #4E79A7;
    color: #C8C8E0;
    selection-background-color: #2D3A6A;
}

/* ── LineEdit ── */
QLineEdit {
    background: #0E0E20;
    border: 1px solid #2A2A45;
    border-radius: 5px;
    color: #C8C8E0;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 28px;
}
QLineEdit:focus { border-color: #4E79A7; }

/* ── Botones primarios ── */
QPushButton#btn_primary {
    background: #4E79A7;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#btn_primary:hover    { background: #5A8BBF; }
QPushButton#btn_primary:pressed  { background: #3D6085; }
QPushButton#btn_primary:disabled { background: #2A2A45; color: #555570; }

/* ── Botón convertir (grande) ── */
QPushButton#btn_convertir {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #F28E2B, stop:1 #E07A1A);
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
}
QPushButton#btn_convertir:hover    { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #F9A54A, stop:1 #F28E2B); }
QPushButton#btn_convertir:pressed  { background: #C97018; }
QPushButton#btn_convertir:disabled { background: #2A2A45; color: #555570; }

/* ── Botón cancelar ── */
QPushButton#btn_cancelar {
    background: transparent;
    color: #7A7A9A;
    border: 1px solid #2A2A45;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 13px;
}
QPushButton#btn_cancelar:hover    { border-color: #E05A5A; color: #E05A5A; }
QPushButton#btn_cancelar:disabled { color: #333350; border-color: #1A1A32; }

/* ── Botones ghost (quitar, carpeta) ── */
QPushButton#btn_ghost {
    background: transparent;
    color: #7A7A9A;
    border: 1px solid #2A2A45;
    border-radius: 5px;
    padding: 5px 12px;
    font-size: 11px;
}
QPushButton#btn_ghost:hover { border-color: #4E79A7; color: #4E79A7; }

/* ── Progress bar ── */
QProgressBar {
    background: #0E0E20;
    border: 1px solid #2A2A45;
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #F28E2B, stop:1 #4E79A7);
    border-radius: 6px;
}

/* ── Labels ── */
QLabel { color: #9090B0; font-size: 11px; }
QLabel#val_label { color: #C8C8E0; font-size: 12px; }

/* ── Status bar ── */
QStatusBar { background: #12122A; color: #5A5A7A; font-size: 11px; border-top: 1px solid #2A2A45; }

/* ── Separador ── */
QFrame#sep { background: #2A2A45; }

/* ── GroupBox ── */
QGroupBox {
    color: #7A7A9A;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    border: 1px solid #2A2A45;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 10px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #4E79A7; }
"""


class VentanaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("txt2media")
        self.setMinimumSize(QSize(860, 600))
        self.resize(960, 660)
        self.setAcceptDrops(True)
        self._worker = None
        self._archivos: list[Path] = []
        self.setStyleSheet(_QSS)
        self._init_ui()

    # ------------------------------------------------------------------ #
    def _init_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ──────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(56)
        h_hdr = QHBoxLayout(header)
        h_hdr.setContentsMargins(24, 0, 24, 0)

        icono = QLabel("▶")
        icono.setStyleSheet("color:#F28E2B; font-size:20px;")
        lbl_titulo = QLabel("txt2media")
        lbl_titulo.setObjectName("app_titulo")
        lbl_ver = QLabel("v1.0.1")
        lbl_ver.setObjectName("app_version")

        h_hdr.addWidget(icono)
        h_hdr.addSpacing(8)
        h_hdr.addWidget(lbl_titulo)
        h_hdr.addSpacing(8)
        h_hdr.addWidget(lbl_ver)
        h_hdr.addStretch()

        self.lbl_archivo_actual = QLabel("")
        self.lbl_archivo_actual.setStyleSheet("color:#5A5A7A; font-size:11px;")
        h_hdr.addWidget(self.lbl_archivo_actual)
        root.addWidget(header)

        # ── Cuerpo: izquierda + derecha ──────────────────────────────────
        cuerpo = QWidget()
        h_cuerpo = QHBoxLayout(cuerpo)
        h_cuerpo.setSpacing(0)
        h_cuerpo.setContentsMargins(0, 0, 0, 0)

        # ── Panel izquierdo (archivos) ───────────────────────────────────
        panel_izq = QWidget()
        panel_izq.setObjectName("panel_izq")
        panel_izq.setMinimumWidth(360)
        panel_izq.setMaximumWidth(480)
        v_izq = QVBoxLayout(panel_izq)
        v_izq.setContentsMargins(20, 20, 20, 20)
        v_izq.setSpacing(10)

        lbl_arch = QLabel("ARCHIVOS DE ENTRADA")
        lbl_arch.setObjectName("sec_label")
        v_izq.addWidget(lbl_arch)

        self.lista_archivos = QListWidget()
        self.lista_archivos.setMinimumHeight(200)
        self.lista_archivos.setAlternatingRowColors(False)
        v_izq.addWidget(self.lista_archivos)

        h_btns = QHBoxLayout()
        self.btn_agregar = QPushButton("+ Agregar archivos")
        self.btn_agregar.setObjectName("btn_primary")
        self.btn_quitar = QPushButton("Quitar")
        self.btn_quitar.setObjectName("btn_ghost")
        h_btns.addWidget(self.btn_agregar)
        h_btns.addWidget(self.btn_quitar)
        h_btns.addStretch()
        v_izq.addLayout(h_btns)

        # Drop hint
        lbl_drop = QLabel("O arrastra archivos EPUB · PDF · DOCX · MD")
        lbl_drop.setStyleSheet("color:#333355; font-size:10px; padding-top:4px;")
        v_izq.addWidget(lbl_drop)
        v_izq.addStretch()

        h_cuerpo.addWidget(panel_izq)

        # ── Separador vertical ───────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("sep")
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        h_cuerpo.addWidget(sep)

        # ── Panel derecho (opciones + acción) ────────────────────────────
        panel_der = QWidget()
        v_der = QVBoxLayout(panel_der)
        v_der.setContentsMargins(28, 24, 28, 24)
        v_der.setSpacing(16)

        lbl_opc = QLabel("OPCIONES DE CONVERSIÓN")
        lbl_opc.setObjectName("sec_label")
        v_der.addWidget(lbl_opc)

        # Formato
        v_der.addWidget(QLabel("Formato de salida"))
        self.combo_formato = QComboBox()
        formatos = [
            ("PPTX — Presentación PowerPoint", "pptx"),
            ("DOCX — Documento Word",          "docx"),
            ("XLSX — Hoja de cálculo Excel",   "xlsx"),
            ("MP3  — Audio narrado",           "audio"),
            ("MP4  — Video con diapositivas",  "video"),
            ("MD   — Markdown enriquecido",    "md"),
            ("HTML — Página web con menú",     "html"),
        ]
        for label, data in formatos:
            self.combo_formato.addItem(label, data)
        v_der.addWidget(self.combo_formato)

        # Modo audio
        self.lbl_modo = QLabel("Modo audio")
        v_der.addWidget(self.lbl_modo)
        self.combo_modo = QComboBox()
        self.combo_modo.addItem("Completo — un archivo MP3",   "completo")
        self.combo_modo.addItem("Por capítulos — BookPlayer",  "capitulos")
        v_der.addWidget(self.combo_modo)

        # Voz TTS
        self.lbl_voz = QLabel("Voz TTS")
        v_der.addWidget(self.lbl_voz)
        self.combo_voz = QComboBox()
        self.combo_voz.addItem("Camila — es-PE (femenina)",  "es-PE-CamilaNeural")
        self.combo_voz.addItem("Alex   — es-PE (masculina)", "es-PE-AlexNeural")
        v_der.addWidget(self.combo_voz)

        # Carpeta salida
        v_der.addWidget(QLabel("Carpeta de salida"))
        h_sal = QHBoxLayout()
        self.edit_salida = QLineEdit(".")
        btn_carpeta = QPushButton("…")
        btn_carpeta.setObjectName("btn_ghost")
        btn_carpeta.setFixedWidth(36)
        h_sal.addWidget(self.edit_salida)
        h_sal.addWidget(btn_carpeta)
        v_der.addLayout(h_sal)

        v_der.addStretch()

        # ── Área de acción ────────────────────────────────────────────────
        sep2 = QFrame()
        sep2.setObjectName("sep")
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        v_der.addWidget(sep2)

        # Progress
        self.lbl_progreso = QLabel("Listo para convertir")
        self.lbl_progreso.setStyleSheet("color:#5A5A7A; font-size:11px;")
        v_der.addWidget(self.lbl_progreso)

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)
        self.barra_progreso.setFixedHeight(8)
        self.barra_progreso.setTextVisible(False)
        v_der.addWidget(self.barra_progreso)

        # Botones
        h_acc = QHBoxLayout()
        self.btn_convertir = QPushButton("Convertir")
        self.btn_convertir.setObjectName("btn_convertir")
        self.btn_convertir.setMinimumHeight(44)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.setMinimumHeight(44)
        h_acc.addWidget(self.btn_convertir, 3)
        h_acc.addWidget(self.btn_cancelar, 1)
        v_der.addLayout(h_acc)

        h_cuerpo.addWidget(panel_der, 1)
        root.addWidget(cuerpo, 1)

        # ── Status bar ────────────────────────────────────────────────────
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Listo  ·  txt2media v1.0.1")

        # ── Conexiones ───────────────────────────────────────────────────
        self.btn_agregar.clicked.connect(self._agregar_archivos)
        self.btn_quitar.clicked.connect(self._quitar_archivo)
        btn_carpeta.clicked.connect(self._seleccionar_carpeta)
        self.btn_convertir.clicked.connect(self._iniciar_conversion)
        self.btn_cancelar.clicked.connect(self._cancelar_conversion)
        self.combo_formato.currentIndexChanged.connect(self._on_formato_cambiado)
        self._on_formato_cambiado()

    # ------------------------------------------------------------------ #
    def _on_formato_cambiado(self) -> None:
        fmt = self.combo_formato.currentData()
        es_audio = fmt == "audio"
        tiene_voz = fmt in ("audio", "video")
        self.lbl_modo.setVisible(es_audio)
        self.combo_modo.setVisible(es_audio)
        self.lbl_voz.setVisible(tiene_voz)
        self.combo_voz.setVisible(tiene_voz)

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

    def _agregar_archivos(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos", "",
            "Documentos (*.epub *.pdf *.docx *.md);;Todos (*)",
        )
        for p in paths:
            self._agregar_path(Path(p))

    def _agregar_path(self, path: Path) -> None:
        if path not in self._archivos:
            self._archivos.append(path)
            icono = _EXT_ICONOS.get(path.suffix.lower(), "📄")
            try:
                size_kb = path.stat().st_size // 1024
                label = f"{icono}  {path.name}   {size_kb} KB"
            except OSError:
                label = f"{icono}  {path.name}"
            item = QListWidgetItem(label)
            self.lista_archivos.addItem(item)

    def _quitar_archivo(self) -> None:
        row = self.lista_archivos.currentRow()
        if row >= 0:
            self.lista_archivos.takeItem(row)
            self._archivos.pop(row)

    def _seleccionar_carpeta(self) -> None:
        carpeta = QFileDialog.getExistingDirectory(self, "Carpeta de salida")
        if carpeta:
            self.edit_salida.setText(carpeta)

    # ------------------------------------------------------------------ #
    def _iniciar_conversion(self) -> None:
        if not self._archivos:
            QMessageBox.warning(self, "Sin archivos", "Agrega al menos un archivo.")
            return

        from txt2media.ui.worker_conversion import WorkerConversion

        fmt    = self.combo_formato.currentData()
        modo   = self.combo_modo.currentData()
        voz    = self.combo_voz.currentData()
        carpeta = Path(self.edit_salida.text() or ".")

        self._worker = WorkerConversion(
            archivos=self._archivos, formato=fmt,
            carpeta_salida=carpeta, voz=voz, modo=modo,
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
        self.lbl_progreso.setText("Cancelando…")

    def _on_progreso(self, actual: int, total: int, nombre: str) -> None:
        if actual == 0:
            self.barra_progreso.setRange(0, 0)
        else:
            self.barra_progreso.setRange(0, 100)
            pct = int(actual / total * 100) if total else 0
            self.barra_progreso.setValue(pct)
        self.lbl_progreso.setText(f"[{actual}/{total}]  {nombre}")
        self.lbl_archivo_actual.setText(nombre)
        self.status.showMessage(f"Convirtiendo  {actual}/{total}  —  {nombre}")

    def _on_completado(self, resultados: list) -> None:
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(100)
        self.btn_convertir.setEnabled(True)
        self.btn_cancelar.setEnabled(False)
        n = len(resultados)
        self.lbl_progreso.setText(f"✓  {n} archivo(s) generado(s)")
        self.lbl_archivo_actual.setText("")
        self.status.showMessage(f"Completado  ·  {n} archivo(s)  →  {self.edit_salida.text()}")
        QMessageBox.information(
            self, "Completado",
            f"Se generaron {n} archivo(s).\n\nCarpeta: {self.edit_salida.text()}",
        )

    def _on_error(self, mensaje: str) -> None:
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)
        self.lbl_progreso.setText("Error en la conversión")
        self.lbl_archivo_actual.setText("")
        self.btn_convertir.setEnabled(True)
        self.btn_cancelar.setEnabled(False)
        self.status.showMessage(f"Error  ·  {mensaje[:80]}")
        QMessageBox.critical(self, "Error", mensaje)


def lanzar_app() -> None:
    if not _PYSIDE6_OK:
        try:
            import tkinter.messagebox as mb
            mb.showerror("txt2media", "PySide6 no instalado.\nEjecuta instalar.bat primero.")
        except Exception:
            pass
        return
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    lanzar_app()
