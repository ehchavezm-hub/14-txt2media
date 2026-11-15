@echo off
cd /d "%~dp0"
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "%PYCMD%"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "%PYCMD%"=="" ( echo Python no encontrado. & pause & exit /b 1 )

echo === TEST VIDEO txt2media ===
echo.

echo [1] ffmpeg en PATH:
where ffmpeg
ffmpeg -version 2>&1 | findstr "ffmpeg version"
echo.

echo [2] Probando generacion de video...
%PYCMD% -c "
import sys, traceback
from pathlib import Path

pdf = list(Path('.').glob('*.pdf'))
if not pdf:
    print('ERROR: No hay PDF en esta carpeta')
    sys.exit(1)

archivo = pdf[0]
print(f'Archivo: {archivo}')
salida = Path('test_output.mp4')

try:
    from txt2media.lectores.lector_pdf import LectorPDF
    doc = LectorPDF().leer(archivo)
    print(f'Secciones leidas: {len(doc.secciones)}')
except Exception as e:
    print(f'ERROR al leer PDF: {e}')
    traceback.print_exc()
    sys.exit(1)

try:
    from txt2media.generadores.generador_video import GeneradorVideo
    gen = GeneradorVideo()
    gen.generar(doc, salida)
    print(f'VIDEO GENERADO: {salida} ({salida.stat().st_size/1024/1024:.1f} MB)')
except Exception as e:
    print(f'ERROR al generar video: {e}')
    traceback.print_exc()
    sys.exit(1)
"
echo.
pause
