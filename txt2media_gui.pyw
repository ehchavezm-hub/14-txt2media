# txt2media_gui.pyw — Doble clic para abrir la GUI sin consola DOS
# Windows abre .pyw con pythonw.exe automaticamente (sin ventana negra)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from txt2media.ui.ventana_principal import lanzar_app

lanzar_app()
