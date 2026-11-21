"""Ventana principal txt2media — interfaz minimalista PySide6.

Dirección visual: panel de instrumento en tema claro. Fondo blanco, líneas finas, un único
color de señal (azul hielo) reservado para foco, selección y progreso. Texto en
Figtree; datos (formatos, tamaños, estado) en monoespaciada.
"""

from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtCore import QSettings, QSize, Qt, Signal
    from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFontDatabase
    from PySide6.QtWidgets import (
        QApplication, QButtonGroup, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
        QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
        QProgressBar, QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
    )
    _PYSIDE6_OK = True
except ImportError:
    _PYSIDE6_OK = False

_VERSION = "1.0.1"
_EXTENSIONES = (".epub", ".pdf", ".docx", ".md")

# ── Tokens de diseño ───────────────────────────────────────────────────────
_C = {
    "fondo":      "#FFFFFF",
    "panel":      "#F5F6F8",
    "elevado":    "#EEF3FB",
    "linea":      "#E3E6EB",
    "linea_2":    "#CBD1D9",
    "texto":      "#12171D",
    "texto_2":    "#4E5865",
    "texto_3":    "#8A939E",
    "senal":      "#1F64D6",
    "ok":         "#1E9A68",
    "error":      "#D14343",
}
_SANS = "'Figtree', 'Segoe UI', 'Inter', sans-serif"
_MONO = "'Cascadia Mono', 'Consolas', 'JetBrains Mono', 'DejaVu Sans Mono', monospace"

_FORMATOS_DOC = [
    ("PPTX", "Presentación", "pptx"),
    ("DOCX", "Word", "docx"),
    ("XLSX", "Excel", "xlsx"),
    ("MD", "Markdown", "md"),
    ("HTML", "Página web", "html"),
]
_FORMATOS_MEDIO = [
    ("MP3", "Audio narrado", "audio"),
    ("MP4", "Video narrado", "video"),
]
_NOMBRE_FORMATO = {d: c for c, _, d in _FORMATOS_DOC + _FORMATOS_MEDIO}

_QSS = f"""
* {{ font-family: {_SANS}; outline: none; }}
QMainWindow, QWidget#central {{ background: {_C['fondo']}; }}
QLabel {{ color: {_C['texto_2']}; font-size: 13px; background: transparent; }}

/* Barra superior */
QWidget#barra_sup {{ background: {_C['fondo']}; border-bottom: 1px solid {_C['linea']}; }}
QLabel#marca {{ color: {_C['texto']}; font-size: 16px; font-weight: 700; letter-spacing: 0.3px; }}
QLabel#version {{ color: {_C['texto_3']}; font-family: {_MONO}; font-size: 11px; }}
QLabel#estado {{ color: {_C['texto_2']}; font-family: {_MONO}; font-size: 11px; letter-spacing: 1.5px; }}
QLabel#punto {{ border-radius: 4px; background: {_C['texto_3']}; }}
QLabel#punto[estado="trabajando"] {{ background: {_C['senal']}; }}
QLabel#punto[estado="ok"] {{ background: {_C['ok']}; }}
QLabel#punto[estado="error"] {{ background: {_C['error']}; }}

/* Paneles y encabezados de sección */
QWidget#panel_izq {{ background: {_C['panel']}; border-right: 1px solid {_C['linea']}; }}
QLabel#paso {{ color: {_C['texto_3']}; font-family: {_MONO}; font-size: 11px; }}
QLabel#titulo_sec {{ color: {_C['texto']}; font-size: 15px; font-weight: 600; }}
QLabel#etiqueta {{ color: {_C['texto_3']}; font-family: {_MONO}; font-size: 10px; letter-spacing: 1.5px; }}
QLabel#dato {{ color: {_C['texto_3']}; font-family: {_MONO}; font-size: 11px; }}

/* Zona de arrastre (estado vacío) */
QFrame#zona {{ border: 1px dashed {_C['linea_2']}; border-radius: 10px; background: transparent; }}
QFrame#zona[arrastrando="true"] {{ border: 1px solid {_C['senal']}; background: {_C['elevado']}; }}
QLabel#zona_titulo {{ color: {_C['texto']}; font-size: 15px; font-weight: 600; }}
QLabel#zona_sub {{ color: {_C['texto_3']}; font-family: {_MONO}; font-size: 11px; letter-spacing: 1px; }}

/* Lista de archivos */
QListWidget#lista {{ background: transparent; border: none; }}
QListWidget#lista::item {{ border-bottom: 1px solid {_C['linea']}; }}
QListWidget#lista::item:selected {{ background: {_C['elevado']}; }}
QListWidget#lista {{ background: {_C['fondo']}; border: 1px solid {_C['linea']}; border-radius: 8px; }}
QListWidget#lista::item:hover {{ background: {_C['elevado']}; }}
QLabel#fila_tipo {{ color: {_C['texto_2']}; font-family: {_MONO}; font-size: 10px; letter-spacing: 1px;
    border: 1px solid {_C['linea_2']}; border-radius: 3px; padding: 1px 0; }}
QLabel#fila_nombre {{ color: {_C['texto']}; font-size: 13px; }}
QLabel#fila_peso {{ color: {_C['texto_3']}; font-family: {_MONO}; font-size: 11px; }}
QPushButton#fila_quitar {{ color: {_C['texto_3']}; background: transparent; border: none; font-size: 15px;
    border-radius: 4px; }}
QPushButton#fila_quitar:hover {{ color: {_C['texto']}; background: {_C['linea_2']}; }}

/* Botones */
QPushButton {{ font-size: 13px; }}
QPushButton#primario {{ background: {_C['texto']}; color: {_C['fondo']}; border: none; border-radius: 6px;
    padding: 0 22px; font-weight: 600; min-height: 38px; }}
QPushButton#primario:hover {{ background: #000000; }}
QPushButton#primario:pressed {{ background: #2B323B; }}
QPushButton#primario:focus {{ border: 2px solid {_C['senal']}; }}
QPushButton#primario:disabled {{ background: {_C['linea']}; color: {_C['texto_3']}; }}
QPushButton#secundario {{ background: transparent; color: {_C['texto_2']}; border: 1px solid {_C['linea_2']};
    border-radius: 6px; padding: 0 14px; min-height: 32px; }}
QPushButton#secundario:hover {{ color: {_C['texto']}; border-color: {_C['texto_3']}; }}
QPushButton#secundario:focus {{ border-color: {_C['texto_2']}; }}
QPushButton#enlace {{ background: transparent; color: {_C['texto_3']}; border: none; padding: 4px 6px; font-size: 12px; }}
QPushButton#enlace:hover {{ color: {_C['texto']}; }}

/* Selectores: mosaicos de formato y segmentos */
QPushButton#mosaico, QPushButton#segmento {{ background: transparent; border: 1px solid {_C['linea']};
    border-radius: 6px; text-align: left; }}
QPushButton#mosaico {{ min-height: 58px; }}
QPushButton#segmento {{ min-height: 34px; padding: 0 14px; color: {_C['texto_2']}; text-align: center; }}
QPushButton#mosaico:hover, QPushButton#segmento:hover {{ border-color: {_C['linea_2']}; background: {_C['panel']}; }}
QPushButton#mosaico:checked, QPushButton#segmento:checked {{ border-color: {_C['senal']}; background: {_C['elevado']}; }}
QPushButton#segmento:checked {{ color: {_C['texto']}; }}
QPushButton#mosaico:focus, QPushButton#segmento:focus {{ border-color: {_C['texto_2']}; }}
QPushButton#mosaico:checked:focus, QPushButton#segmento:checked:focus {{ border-color: {_C['senal']}; }}
QLabel#mosaico_cod {{ color: {_C['texto_2']}; font-family: {_MONO}; font-size: 13px; font-weight: 600; letter-spacing: 1px; }}
QLabel#mosaico_cod[activo="true"] {{ color: {_C['senal']}; }}
QLabel#mosaico_txt {{ color: {_C['texto_3']}; font-size: 11px; }}
QLabel#mosaico_txt[activo="true"] {{ color: {_C['texto_2']}; }}

/* Campo de carpeta */
QLineEdit {{ background: {_C['fondo']}; border: 1px solid {_C['linea']}; border-radius: 6px; color: {_C['texto']};
    padding: 0 12px; min-height: 34px; font-family: {_MONO}; font-size: 12px;
    selection-background-color: {_C['linea_2']}; }}
QLineEdit:hover {{ border-color: {_C['linea_2']}; }}
QLineEdit:focus {{ border-color: {_C['senal']}; }}

/* Barra de acción */
QWidget#barra_acc {{ background: {_C['panel']}; border-top: 1px solid {_C['linea']}; }}
QLabel#progreso_txt {{ color: {_C['texto_2']}; font-family: {_MONO}; font-size: 12px; }}
QProgressBar {{ background: transparent; border: none; max-height: 2px; }}
QProgressBar::chunk {{ background: {_C['senal']}; }}

QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {_C['linea_2']}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QToolTip {{ background: {_C['elevado']}; color: {_C['texto']}; border: 1px solid {_C['linea_2']}; padding: 4px 8px; }}
"""


def _cargar_fuentes() -> None:
    """Registra Figtree desde recursos/fuentes; si falta, Qt usa la alternativa."""
    try:
        from txt2media.utils.recursos import get_recurso
        for nombre in ("Figtree-Regular.ttf", "Figtree-Bold.ttf"):
            ruta = get_recurso(f"fuentes/{nombre}")
            if ruta.exists():
                QFontDatabase.addApplicationFont(str(ruta))
    except Exception:
        pass


def _peso_legible(n_bytes: int) -> str:
    if n_bytes < 1024 * 1024:
        return f"{max(1, n_bytes // 1024)} KB"
    return f"{n_bytes / (1024 * 1024):.1f} MB"


def _repulir(widget: "QWidget") -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


if _PYSIDE6_OK:

    class _Selector(QWidget):
        """Grupo de botones exclusivos con la misma API básica que QComboBox."""

        currentIndexChanged = Signal(int)

        def __init__(self, filas: list, columnas: int, mosaico: bool) -> None:
            super().__init__()
            self._datos: list[str] = []
            self._botones: list[QPushButton] = []
            self._grupo = QButtonGroup(self)
            self._grupo.setExclusive(True)
            rejilla = QGridLayout(self)
            rejilla.setContentsMargins(0, 0, 0, 0)
            rejilla.setHorizontalSpacing(8)
            rejilla.setVerticalSpacing(8)
            fila_grid = 0
            for etiqueta, opciones in filas:
                if etiqueta:
                    lbl = QLabel(etiqueta)
                    lbl.setObjectName("etiqueta")
                    rejilla.addWidget(lbl, fila_grid, 0, 1, columnas)
                    fila_grid += 1
                for col, (codigo, texto, dato) in enumerate(opciones):
                    btn = self._crear_boton(codigo, texto, mosaico)
                    idx = len(self._botones)
                    self._grupo.addButton(btn, idx)
                    self._botones.append(btn)
                    self._datos.append(dato)
                    rejilla.addWidget(btn, fila_grid, col)
                fila_grid += 1
            for c in range(columnas):
                rejilla.setColumnStretch(c, 1)
            self._grupo.idToggled.connect(self._al_cambiar)
            if self._botones:
                self._botones[0].setChecked(True)

        def _crear_boton(self, codigo: str, texto: str, mosaico: bool) -> "QPushButton":
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            if not mosaico:
                btn.setObjectName("segmento")
                btn.setText(texto)
                return btn
            btn.setObjectName("mosaico")
            btn.setAccessibleName(f"{codigo} — {texto}")
            caja = QVBoxLayout(btn)
            caja.setContentsMargins(12, 9, 12, 9)
            caja.setSpacing(2)
            for nombre, contenido in (("mosaico_cod", codigo), ("mosaico_txt", texto)):
                lbl = QLabel(contenido)
                lbl.setObjectName(nombre)
                lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                caja.addWidget(lbl)
            return btn

        def _al_cambiar(self, idx: int, marcado: bool) -> None:
            for lbl in self._botones[idx].findChildren(QLabel):
                lbl.setProperty("activo", marcado)
                _repulir(lbl)
            if marcado:
                self.currentIndexChanged.emit(idx)

        # API compatible con QComboBox
        def currentIndex(self) -> int:
            return self._grupo.checkedId()

        def currentData(self) -> str:
            idx = self.currentIndex()
            return self._datos[idx] if idx >= 0 else ""

        def findData(self, dato: str) -> int:
            return self._datos.index(dato) if dato in self._datos else -1

        def setCurrentIndex(self, idx: int) -> None:
            if 0 <= idx < len(self._botones):
                self._botones[idx].setChecked(True)

        def count(self) -> int:
            return len(self._botones)

    class _FilaArchivo(QWidget):
        quitar = Signal(object)

        def __init__(self, ruta: Path) -> None:
            super().__init__()
            self.ruta = ruta
            caja = QHBoxLayout(self)
            caja.setContentsMargins(12, 0, 6, 0)
            caja.setSpacing(12)

            tipo = QLabel(ruta.suffix.lstrip(".").upper())
            tipo.setObjectName("fila_tipo")
            tipo.setFixedSize(42, 20)
            tipo.setAlignment(Qt.AlignmentFlag.AlignCenter)

            nombre = QLabel(ruta.name)
            nombre.setObjectName("fila_nombre")
            nombre.setToolTip(str(ruta))
            nombre.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

            try:
                peso_txt = _peso_legible(ruta.stat().st_size)
            except OSError:
                peso_txt = "—"
            peso = QLabel(peso_txt)
            peso.setObjectName("fila_peso")
            peso.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            btn = QPushButton("×")
            btn.setObjectName("fila_quitar")
            btn.setFixedSize(26, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip("Quitar de la lista")
            btn.setAccessibleName(f"Quitar {ruta.name}")
            btn.clicked.connect(lambda: self.quitar.emit(self.ruta))

            caja.addWidget(tipo)
            caja.addWidget(nombre, 1)
            caja.addWidget(peso)
            caja.addWidget(btn)

    class _ZonaArrastre(QFrame):
        def __init__(self, al_pulsar) -> None:
            super().__init__()
            self.setObjectName("zona")
            caja = QVBoxLayout(self)
            caja.setContentsMargins(24, 24, 24, 24)
            caja.setSpacing(6)
            caja.addStretch()
            titulo = QLabel("Arrastra documentos aquí")
            titulo.setObjectName("zona_titulo")
            sub = QLabel("EPUB  ·  PDF  ·  DOCX  ·  MD")
            sub.setObjectName("zona_sub")
            for w in (titulo, sub):
                w.setAlignment(Qt.AlignmentFlag.AlignCenter)
                caja.addWidget(w)
            caja.addSpacing(14)
            btn = QPushButton("Seleccionar archivos")
            btn.setObjectName("secundario")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(al_pulsar)
            fila = QHBoxLayout()
            fila.addStretch()
            fila.addWidget(btn)
            fila.addStretch()
            caja.addLayout(fila)
            caja.addStretch()

        def marcar(self, activo: bool) -> None:
            self.setProperty("arrastrando", activo)
            _repulir(self)


def _encabezado(paso: str, titulo: str) -> "QWidget":
    w = QWidget()
    caja = QHBoxLayout(w)
    caja.setContentsMargins(0, 0, 0, 0)
    caja.setSpacing(10)
    lbl_paso = QLabel(paso)
    lbl_paso.setObjectName("paso")
    lbl_tit = QLabel(titulo)
    lbl_tit.setObjectName("titulo_sec")
    caja.addWidget(lbl_paso)
    caja.addWidget(lbl_tit)
    caja.addStretch()
    return w


class VentanaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        _cargar_fuentes()
        self.setWindowTitle("txt2media")
        self.setMinimumSize(QSize(920, 620))
        self.resize(1040, 680)
        self.setAcceptDrops(True)
        self._worker = None
        self._archivos: list[Path] = []
        self._settings = QSettings("txt2media", "txt2media") if _PYSIDE6_OK else None
        self.setStyleSheet(_QSS)
        self._init_ui()
        self._restaurar_ajustes()
        self._actualizar_estado_entrada()

    # ------------------------------------------------------------------ #
    def _init_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        raiz = QVBoxLayout(central)
        raiz.setSpacing(0)
        raiz.setContentsMargins(0, 0, 0, 0)

        raiz.addWidget(self._crear_barra_superior())

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(0)
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.addWidget(self._crear_panel_entrada())
        cuerpo.addWidget(self._crear_panel_salida(), 1)
        raiz.addLayout(cuerpo, 1)

        raiz.addWidget(self._crear_barra_accion())

        self.combo_formato.currentIndexChanged.connect(self._on_formato_cambiado)
        self._on_formato_cambiado()

    def _crear_barra_superior(self) -> "QWidget":
        barra = QWidget()
        barra.setObjectName("barra_sup")
        barra.setFixedHeight(52)
        caja = QHBoxLayout(barra)
        caja.setContentsMargins(24, 0, 24, 0)
        caja.setSpacing(10)
        caja.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        marca = QLabel("txt2media")
        marca.setObjectName("marca")
        version = QLabel(f"v{_VERSION}")
        version.setObjectName("version")
        caja.addWidget(marca)
        caja.addWidget(version)
        caja.addStretch()

        self.punto_estado = QLabel()
        self.punto_estado.setObjectName("punto")
        self.punto_estado.setFixedSize(8, 8)
        self.lbl_estado = QLabel("LISTO")
        self.lbl_estado.setObjectName("estado")
        caja.addWidget(self.punto_estado)
        caja.addWidget(self.lbl_estado)
        return barra

    def _crear_panel_entrada(self) -> "QWidget":
        panel = QWidget()
        panel.setObjectName("panel_izq")
        panel.setFixedWidth(400)
        caja = QVBoxLayout(panel)
        caja.setContentsMargins(24, 24, 24, 20)
        caja.setSpacing(16)

        caja.addWidget(_encabezado("01", "Documentos"))

        self.pila_entrada = QStackedWidget()
        self.zona_arrastre = _ZonaArrastre(self._agregar_archivos)
        self.pila_entrada.addWidget(self.zona_arrastre)

        con_lista = QWidget()
        v = QVBoxLayout(con_lista)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)
        self.lista_archivos = QListWidget()
        self.lista_archivos.setObjectName("lista")
        self.lista_archivos.setFrameShape(QFrame.Shape.NoFrame)
        self.lista_archivos.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        v.addWidget(self.lista_archivos, 1)

        pie = QHBoxLayout()
        pie.setSpacing(4)
        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setObjectName("dato")
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setObjectName("enlace")
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quitar = QPushButton("Quitar")
        self.btn_quitar.setObjectName("enlace")
        self.btn_quitar.setCursor(Qt.CursorShape.PointingHandCursor)
        pie.addWidget(self.lbl_resumen)
        pie.addStretch()
        pie.addWidget(self.btn_agregar)
        pie.addWidget(self.btn_quitar)
        v.addLayout(pie)
        self.pila_entrada.addWidget(con_lista)

        caja.addWidget(self.pila_entrada, 1)

        self.btn_agregar.clicked.connect(self._agregar_archivos)
        self.btn_quitar.clicked.connect(self._quitar_archivo)
        return panel

    def _crear_panel_salida(self) -> "QWidget":
        panel = QWidget()
        caja = QVBoxLayout(panel)
        caja.setContentsMargins(32, 24, 32, 20)
        caja.setSpacing(16)

        caja.addWidget(_encabezado("02", "Formato de salida"))
        self.combo_formato = _Selector(
            [("DOCUMENTO", _FORMATOS_DOC), ("MEDIOS", _FORMATOS_MEDIO)], columnas=5, mosaico=True,
        )
        caja.addWidget(self.combo_formato)

        # Opciones de voz (solo audio y video)
        self.bloque_voz = QWidget()
        v_voz = QVBoxLayout(self.bloque_voz)
        v_voz.setContentsMargins(0, 4, 0, 0)
        v_voz.setSpacing(16)

        self.lbl_voz = QLabel("VOZ  ·  ES-PE")
        self.lbl_voz.setObjectName("etiqueta")
        self.combo_voz = _Selector(
            [(None, [("", "Camila", "es-PE-CamilaNeural"),
                     ("", "Alex", "es-PE-AlexNeural")])],
            columnas=2, mosaico=False,
        )
        self.lbl_modo = QLabel("ARCHIVOS DE AUDIO")
        self.lbl_modo.setObjectName("etiqueta")
        self.combo_modo = _Selector(
            [(None, [("", "Un solo MP3", "completo"),
                     ("", "Un MP3 por capítulo", "capitulos")])],
            columnas=2, mosaico=False,
        )
        fila_opc = QHBoxLayout()
        fila_opc.setSpacing(24)
        for etiqueta, selector in ((self.lbl_voz, self.combo_voz), (self.lbl_modo, self.combo_modo)):
            col = QVBoxLayout()
            col.setSpacing(8)
            col.addWidget(etiqueta)
            col.addWidget(selector)
            fila_opc.addLayout(col, 1)
        self.col_modo = fila_opc.itemAt(1).layout()
        v_voz.addLayout(fila_opc)
        caja.addWidget(self.bloque_voz)

        caja.addSpacing(12)
        caja.addWidget(_encabezado("03", "Destino"))
        fila = QHBoxLayout()
        fila.setSpacing(8)
        self.edit_salida = QLineEdit(".")
        self.edit_salida.setPlaceholderText("Carpeta donde se guardarán los archivos")
        self.edit_salida.setAccessibleName("Carpeta de salida")
        btn_carpeta = QPushButton("Examinar")
        btn_carpeta.setObjectName("secundario")
        btn_carpeta.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_carpeta.clicked.connect(self._seleccionar_carpeta)
        fila.addWidget(self.edit_salida, 1)
        fila.addWidget(btn_carpeta)
        caja.addLayout(fila)

        caja.addStretch()
        return panel

    def _crear_barra_accion(self) -> "QWidget":
        barra = QWidget()
        barra.setObjectName("barra_acc")
        v = QVBoxLayout(barra)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)
        self.barra_progreso.setFixedHeight(2)
        self.barra_progreso.setTextVisible(False)
        v.addWidget(self.barra_progreso)

        fila = QHBoxLayout()
        fila.setContentsMargins(24, 14, 24, 14)
        fila.setSpacing(10)
        self.lbl_progreso = QLabel("")
        self.lbl_progreso.setObjectName("progreso_txt")
        self.lbl_progreso.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        fila.addWidget(self.lbl_progreso, 1)

        self.btn_abrir_carpeta = QPushButton("Abrir carpeta")
        self.btn_abrir_carpeta.setObjectName("secundario")
        self.btn_abrir_carpeta.setVisible(False)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("secundario")
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.setVisible(False)
        self.btn_convertir = QPushButton("Convertir")
        self.btn_convertir.setObjectName("primario")
        self.btn_convertir.setMinimumWidth(200)
        for b in (self.btn_abrir_carpeta, self.btn_cancelar, self.btn_convertir):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            fila.addWidget(b)
        v.addLayout(fila)

        self.btn_convertir.clicked.connect(self._iniciar_conversion)
        self.btn_cancelar.clicked.connect(self._cancelar_conversion)
        self.btn_abrir_carpeta.clicked.connect(self._abrir_carpeta_salida)
        return barra

    # ------------------------------------------------------------------ #
    def _set_estado(self, texto: str, estado: str = "") -> None:
        self.lbl_estado.setText(texto)
        self.punto_estado.setProperty("estado", estado)
        _repulir(self.punto_estado)

    def _trabajando(self) -> bool:
        return bool(self._worker and self._worker.isRunning())

    def _actualizar_estado_entrada(self) -> None:
        n = len(self._archivos)
        self.pila_entrada.setCurrentIndex(1 if n else 0)
        total = 0
        for p in self._archivos:
            try:
                total += p.stat().st_size
            except OSError:
                pass
        self.lbl_resumen.setText(f"{n} {'archivo' if n == 1 else 'archivos'}  ·  {_peso_legible(total)}" if n else "")
        fmt = _NOMBRE_FORMATO.get(self.combo_formato.currentData(), "")
        if n:
            self.btn_convertir.setText(f"Convertir a {fmt}")
        else:
            self.btn_convertir.setText("Convertir")
        self.btn_convertir.setEnabled(not self._trabajando())
        if not self._trabajando():
            self.lbl_progreso.setText(
                "Agrega al menos un documento para empezar" if not n
                else f"{n} {'documento listo' if n == 1 else 'documentos listos'} para convertir a {fmt}"
            )

    def _on_formato_cambiado(self) -> None:
        fmt = self.combo_formato.currentData()
        self.bloque_voz.setVisible(fmt in ("audio", "video"))
        es_audio = fmt == "audio"
        self.lbl_modo.setVisible(es_audio)
        self.combo_modo.setVisible(es_audio)
        self._actualizar_estado_entrada()

    # ------------------------------------------------------------------ #
    def dragEnterEvent(self, event: "QDragEnterEvent") -> None:
        if event.mimeData().hasUrls() and any(
            Path(u.toLocalFile()).suffix.lower() in _EXTENSIONES for u in event.mimeData().urls()
        ):
            event.acceptProposedAction()
            self.zona_arrastre.marcar(True)

    def dragLeaveEvent(self, event) -> None:
        self.zona_arrastre.marcar(False)

    def dropEvent(self, event: "QDropEvent") -> None:
        self.zona_arrastre.marcar(False)
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in _EXTENSIONES:
                self._agregar_path(path)
        event.acceptProposedAction()

    def _agregar_archivos(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar documentos", "",
            "Documentos (*.epub *.pdf *.docx *.md);;Todos (*)",
        )
        for p in paths:
            self._agregar_path(Path(p))

    def _agregar_path(self, path: Path) -> None:
        if path in self._archivos:
            return
        self._archivos.append(path)
        fila = _FilaArchivo(path)
        fila.quitar.connect(self._quitar_ruta)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 46))
        self.lista_archivos.addItem(item)
        self.lista_archivos.setItemWidget(item, fila)
        self._actualizar_estado_entrada()

    def _quitar_ruta(self, ruta: Path) -> None:
        if self._trabajando() or ruta not in self._archivos:
            return
        fila = self._archivos.index(ruta)
        self.lista_archivos.takeItem(fila)
        self._archivos.pop(fila)
        self._actualizar_estado_entrada()

    def _quitar_archivo(self) -> None:
        row = self.lista_archivos.currentRow()
        if 0 <= row < len(self._archivos):
            self._quitar_ruta(self._archivos[row])

    def _seleccionar_carpeta(self) -> None:
        carpeta = QFileDialog.getExistingDirectory(self, "Carpeta de salida")
        if carpeta:
            self.edit_salida.setText(carpeta)

    # ------------------------------------------------------------------ #
    def _iniciar_conversion(self) -> None:
        if self._trabajando():
            return
        if not self._archivos:
            QMessageBox.warning(self, "Sin archivos", "Agrega al menos un archivo.")
            return

        from txt2media.ui.worker_conversion import WorkerConversion

        fmt = self.combo_formato.currentData()
        modo = self.combo_modo.currentData()
        voz = self.combo_voz.currentData()
        carpeta = Path(self.edit_salida.text() or ".")

        self._worker = WorkerConversion(
            archivos=list(self._archivos), formato=fmt,
            carpeta_salida=carpeta, voz=voz, modo=modo,
        )
        self._worker.progreso.connect(self._on_progreso)
        self._worker.completado.connect(self._on_completado)
        self._worker.error.connect(self._on_error)

        self.btn_convertir.setEnabled(False)
        self.btn_cancelar.setEnabled(True)
        self.btn_cancelar.setVisible(True)
        self.btn_abrir_carpeta.setVisible(False)
        self.barra_progreso.setRange(0, 0)
        self.lbl_progreso.setText("Preparando…")
        self._set_estado("PROCESANDO", "trabajando")
        self._worker.start()

    def _cancelar_conversion(self) -> None:
        if self._worker:
            self._worker.cancelar()
        self.btn_cancelar.setEnabled(False)
        self.lbl_progreso.setText("Cancelando…")

    def _on_progreso(self, actual: int, total: int, nombre: str) -> None:
        if actual == 0:
            self.barra_progreso.setRange(0, 0)
        else:
            self.barra_progreso.setRange(0, 100)
            self.barra_progreso.setValue(int(actual / total * 100) if total else 0)
        self.lbl_progreso.setText(f"{actual}/{total}   {nombre}")
        self._set_estado(f"PROCESANDO  {actual}/{total}", "trabajando")

    def _fin_trabajo(self) -> None:
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.setVisible(False)
        self.btn_convertir.setEnabled(True)

    def _on_completado(self, resultados: list) -> None:
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(100)
        self._fin_trabajo()
        n = len(resultados)
        carpeta = self.edit_salida.text() or "."
        destino = "la carpeta actual" if carpeta == "." else carpeta
        self.lbl_progreso.setText(
            f"{n} {'archivo generado' if n == 1 else 'archivos generados'} en {destino}"
        )
        self.lbl_progreso.setToolTip(carpeta)
        self._set_estado("COMPLETADO", "ok")
        self.btn_abrir_carpeta.setVisible(True)
        self._guardar_ajustes()
        QMessageBox.information(
            self, "Completado",
            f"Se generaron {n} archivo(s).\n\nCarpeta: {carpeta}",
        )

    def _on_error(self, mensaje: str) -> None:
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setValue(0)
        self._fin_trabajo()
        self.lbl_progreso.setText("La conversión no se completó. Revisa el detalle del error.")
        self._set_estado("ERROR", "error")
        QMessageBox.critical(self, "Error", mensaje)

    def _abrir_carpeta_salida(self) -> None:
        import subprocess
        import sys
        carpeta = self.edit_salida.text() or "."
        if sys.platform == "win32":
            subprocess.Popen(["explorer", carpeta])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", carpeta])
        else:
            subprocess.Popen(["xdg-open", carpeta])

    def _restaurar_ajustes(self) -> None:
        if not self._settings:
            return
        for clave, selector in (("formato", self.combo_formato), ("voz", self.combo_voz),
                                ("modo", self.combo_modo)):
            valor = self._settings.value(clave, "")
            if valor:
                idx = selector.findData(valor)
                if idx >= 0:
                    selector.setCurrentIndex(idx)
        carpeta = self._settings.value("carpeta_salida", "")
        if carpeta:
            self.edit_salida.setText(carpeta)

    def _guardar_ajustes(self) -> None:
        if not self._settings:
            return
        self._settings.setValue("formato", self.combo_formato.currentData())
        self._settings.setValue("voz", self.combo_voz.currentData())
        self._settings.setValue("modo", self.combo_modo.currentData())
        self._settings.setValue("carpeta_salida", self.edit_salida.text())

    def closeEvent(self, event) -> None:
        self._guardar_ajustes()
        if self._trabajando():
            self._worker.cancelar()
            self._worker.wait(3000)
        super().closeEvent(event)


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
