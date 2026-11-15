@echo off
REM abrir_gui.bat — Abre la interfaz grafica
cd /d "%~dp0"

set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "%PYCMD%"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "%PYCMD%"=="" py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12
if "%PYCMD%"=="" (
    echo Python no encontrado. Ejecuta instalar.bat primero.
    pause & exit /b 1
)

%PYCMD% "%~dp0_lanzar_gui.py"
