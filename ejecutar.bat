@echo off
setlocal enabledelayedexpansion
title txt2media — Ejecutar con Python
cd /d "%~dp0"

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

REM ── 2. Instalar / actualizar dependencias ────────────────────────────────────
echo  [1/2] Instalando dependencias (puede tardar la primera vez)...
echo.

!PYCMD! -m pip install --upgrade pip -q
if errorlevel 1 (
    echo  [AVISO] No se pudo actualizar pip, continuando...
)

!PYCMD! -m pip install -e "%~dp0." -q
if errorlevel 1 (
    echo.
    echo  [ERROR] Fallo la instalacion de dependencias.
    echo   Verifica tu conexion a internet e intenta de nuevo.
    echo.
    pause & exit /b 1
)

echo  Dependencias OK.
echo.

REM ── 3. Lanzar app ────────────────────────────────────────────────────────────
echo  [2/2] Iniciando txt2media...
echo.

REM Intentar sin ventana de consola (pythonw)
set PYCMD_W=!PYCMD:py=pythonw!
start "" !PYCMD_W! "%~dp0lanzar.pyw" >nul 2>&1
if errorlevel 1 (
    REM Fallback con consola visible
    start "" !PYCMD! "%~dp0lanzar.pyw"
)

exit /b 0
