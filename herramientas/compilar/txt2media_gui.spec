# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec para txt2media-gui v1.0.1 (ventana Windows, sin consola)

import sys
from pathlib import Path

# El spec vive en herramientas/compilar: la raíz del repositorio está dos niveles arriba
ROOT = Path(SPECPATH).resolve().parents[1]

block_cipher = None

a = Analysis(
    [str(ROOT / 'src/txt2media/ui/ventana_principal.py')],
    pathex=[str((ROOT / 'src'))],
    binaries=[],
    datas=[
        (str(ROOT / 'recursos'), 'recursos'),
    ],
    hiddenimports=[
        'txt2media',
        'txt2media.cli',
        'txt2media.cli.main',
        'txt2media.core',
        'txt2media.core.modelo',
        'txt2media.core.modo_local',
        'txt2media.core.base_voz',
        'txt2media.core.configuracion',
        'txt2media.core.tema',
        'txt2media.core.resumen_local',
        'txt2media.core.cuota_voz',
        'txt2media.core.renderizador',
        'txt2media.core.orquestador',
        'txt2media.lectores',
        'txt2media.lectores.lector_md',
        'txt2media.lectores.lector_docx',
        'txt2media.lectores.lector_epub',
        'txt2media.lectores.lector_pdf',
        'txt2media.generadores',
        'txt2media.generadores.generador_pptx',
        'txt2media.generadores.generador_docx',
        'txt2media.generadores.generador_xlsx',
        'txt2media.generadores.generador_audio',
        'txt2media.generadores.generador_video',
        'txt2media.motores',
        'txt2media.motores.motor_azure',
        'txt2media.motores.motor_edge_tts',
        'txt2media.motores.motor_sapi',
        'txt2media.motores.cadena_voz',
        'txt2media.utils',
        'txt2media.utils.rutas',
        'txt2media.utils.logging_config',
        'txt2media.ui',
        'txt2media.ui.ventana_principal',
        'txt2media.ui.worker_conversion',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pdfplumber',
        'pptx', 'pptx.util', 'pptx.dml.color',
        'docx',
        'openpyxl',
        'markdown_it',
        'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
        'httpx',
        'edge_tts',
        'keyring', 'keyring.backends', 'keyring.backends.Windows',
        'bs4',
        'defusedxml', 'defusedxml.ElementTree',
        'lxml', 'lxml.etree',
        'langdetect',
        'jsonschema',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'jupyter', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='txt2media-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,        # SIN ventana DOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='txt2media-gui',
)
