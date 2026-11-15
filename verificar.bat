@echo off
REM verificar.bat — Verifica la instalación de txt2media v1.0.1
echo =================================================
echo  txt2media v1.0.1 — Verificación del sistema
echo =================================================

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontró el lanzador de Python (py).
    echo         Instala Python 3.12 o 3.13 desde https://python.org
    exit /b 1
)

echo.
echo [1/5] Versión de Python:
py -3.13 --version 2>nul || py --version

echo.
echo [2/5] Versión de txt2media:
py -3.13 -m txt2media.cli.main --version 2>nul || (
    echo [WARN] txt2media no instalado. Ejecuta: py -3.13 -m pip install -e .
)

echo.
echo [3/5] Verificando ffmpeg:
where ffmpeg >nul 2>&1 && echo [OK] ffmpeg encontrado || echo [WARN] ffmpeg no encontrado. Video deshabilitado.

echo.
echo [4/5] Información del sistema:
py -3.13 -m txt2media.cli.main info 2>nul || echo [WARN] No se pudo obtener información.

echo.
echo [5/5] Ejecutando pruebas rápidas:
py -3.13 -m pytest tests/test_version.py tests/test_modelo.py -v --tb=short 2>nul || (
    echo [WARN] pytest no disponible o tests fallaron.
    echo         Instala: py -3.13 -m pip install pytest
)

echo.
echo =================================================
echo  Verificación completada.
echo  Uso: py -3.13 -m txt2media.cli.main convertir archivo.pdf --formato pptx
echo =================================================
pause
