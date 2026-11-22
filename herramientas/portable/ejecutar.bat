@echo off
setlocal enabledelayedexpansion
title txt2media — Ejecutar con Python
REM En el ZIP portable el proyecto esta al lado; en el repositorio, dos niveles arriba.
set "RAIZ=%~dp0"
if not exist "%RAIZ%pyproject.toml" set "RAIZ=%~dp0..\..\"
cd /d "%RAIZ%"

echo.
echo  =====================================================
echo   txt2media v1.0.1  -  Ejecutar con Python
echo  =====================================================
echo.

REM ── 1. Detectar Python ───────────────────────────────────────────────────────
set PYCMD=
py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "!PYCMD!"=="" py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12
if "!PYCMD!"=="" py -3.11 --version >nul 2>&1 && set PYCMD=py -3.11
if "!PYCMD!"=="" py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "!PYCMD!"=="" python --version >nul 2>&1 && set PYCMD=python

if "!PYCMD!"=="" (
    echo  [ERROR] Python no encontrado.
    echo.
    echo   Descarga Python 3.13 en: https://www.python.org/downloads/
    echo   Marca "Add Python to PATH" al instalar.
    echo.
    pause & exit /b 1
)

for /f "tokens=*" %%v in ('!PYCMD! --version 2^>^&1') do echo  Python encontrado: %%v
echo.

REM ── 2. Verificar si ya esta instalado ────────────────────────────────────────
echo  [1/2] Verificando instalacion...
!PYCMD! -c "import txt2media.ui.ventana_principal" >nul 2>&1
if not errorlevel 1 (
    echo  Ya instalado. Saltando pip.
    goto :Lanzar
)

REM ── Solo si no esta instalado: instalar dependencias ─────────────────────────
echo  Instalando dependencias (primera vez, puede tardar)...
echo.
REM Un Python recien instalado no trae setuptools, que hace falta para instalar la app.
!PYCMD! -m pip install -q --upgrade pip setuptools wheel --no-warn-script-location
!PYCMD! -m pip install --no-build-isolation -e "%RAIZ%." -q --no-warn-script-location
if errorlevel 1 !PYCMD! -m pip install -e "%RAIZ%." -q --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  [ERROR] No se pudieron instalar las dependencias.
    echo   Si el app ya funcionaba antes, intenta con el EXE:
    echo   https://github.com/ehchavezm-hub/14-txt2media/releases
    echo.
    pause & exit /b 1
)

echo  Dependencias OK.
echo.

:Lanzar

REM ── 3. Lanzar app ────────────────────────────────────────────────────────────
echo  [2/2] Iniciando txt2media...

echo.

REM Se ejecuta con consola: si algo falla, el error queda a la vista.
!PYCMD! "%~dp0lanzar.pyw"
if errorlevel 1 (
    echo.
    echo  [ERROR] txt2media se cerro con un error. El detalle esta arriba.
    echo.
    pause & exit /b 1
)

exit /b 0
