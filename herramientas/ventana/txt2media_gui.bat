@echo off
setlocal enabledelayedexpansion
REM txt2media_gui.bat — Abre la interfaz gráfica sin ventana DOS
REM Doble clic para abrir. También se puede poner en el Escritorio.
cd /d "%~dp0..\.."

REM Detectar Python (preferir 3.14/3.13 — Pillow no soporta 3.15 aun)
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "!PYCMD!"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "!PYCMD!"=="" py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12
if "!PYCMD!"=="" py -3.11 --version >nul 2>&1 && set PYCMD=py -3.11
if "!PYCMD!"=="" py -3.15 --version >nul 2>&1 && set PYCMD=py -3.15
if "!PYCMD!"=="" (
    echo.
    echo [ERROR] Python no encontrado.
    echo.
    echo  Ejecuta  instalar_universal.bat  para instalarlo automaticamente.
    echo  Descarga manual: https://www.python.org/downloads/
    echo  (Marca "Add Python to PATH" durante la instalacion)
    echo.
    pause & exit /b 1
)

REM Lanzar GUI sin ventana de consola (pythonw)
set PYCMD_W=%PYCMD: py=pythonw%
for /f "tokens=2 delims=-" %%v in ("%PYCMD%") do set PYVER=%%v

REM Usar start con pythonw para no mostrar consola
start "" pythonw -%PYVER% -m txt2media.ui.ventana_principal 2>nul
if errorlevel 1 (
    REM Fallback: abrir con python normal (mostrará consola brevemente)
    start "" %PYCMD% -m txt2media.ui.ventana_principal
)
