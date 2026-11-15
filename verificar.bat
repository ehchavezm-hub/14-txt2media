@echo off
REM verificar.bat — Verifica la instalación de txt2media v1.0.1
echo =================================================
echo  txt2media v1.0.1 — Verificacion del sistema
echo =================================================

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro el lanzador de Python ^(py^).
    echo         Instala Python desde https://python.org
    pause & exit /b 1
)

REM Detectar version de Python — preferir 3.14/3.13 (Pillow no soporta 3.15 aun)
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "%PYCMD%"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "%PYCMD%"=="" py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12
if "%PYCMD%"=="" py -3.15 --version >nul 2>&1 && set PYCMD=py -3.15
if "%PYCMD%"=="" (
    echo [ERROR] No se encontro Python 3.12 o superior.
    pause & exit /b 1
)

echo.
echo [1/5] Version de Python detectada:
%PYCMD% --version

echo.
echo [2/5] Version de txt2media:
%PYCMD% -m txt2media.cli.main --version 2>nul || (
    echo [WARN] txt2media no instalado. Ejecuta instalar.bat
)

echo.
echo [3/5] Verificando ffmpeg:
where ffmpeg >nul 2>&1 && echo [OK] ffmpeg encontrado || echo [WARN] ffmpeg no encontrado. Video deshabilitado.

echo.
echo [4/5] Informacion del sistema:
%PYCMD% -m txt2media.cli.main info 2>nul || echo [WARN] No se pudo obtener informacion.

echo.
echo [5/5] Pruebas rapidas:
%PYCMD% -m pytest tests/test_version.py tests/test_modelo.py -v --tb=short 2>nul || (
    echo [WARN] Instala pytest: %PYCMD% -m pip install pytest
)

echo.
echo =================================================
echo  Uso: %PYCMD% -m txt2media.cli.main convertir archivo.pdf --formato pptx
echo =================================================
pause
