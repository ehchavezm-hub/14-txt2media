@echo off
REM abrir_gui.bat — Abre la interfaz grafica sin ventana DOS
REM Doble clic para usar
cd /d "%~dp0"

REM Encontrar pythonw.exe desde el py launcher
for /f "delims=" %%p in ('py -3.14 -c "import sys,pathlib; print(pathlib.Path(sys.executable).parent / 'pythonw.exe')" 2^>nul') do set PYWEXE=%%p
if "%PYWEXE%"=="" for /f "delims=" %%p in ('py -3.13 -c "import sys,pathlib; print(pathlib.Path(sys.executable).parent / 'pythonw.exe')" 2^>nul') do set PYWEXE=%%p
if "%PYWEXE%"=="" for /f "delims=" %%p in ('py -3.12 -c "import sys,pathlib; print(pathlib.Path(sys.executable).parent / 'pythonw.exe')" 2^>nul') do set PYWEXE=%%p

if "%PYWEXE%"=="" (
    echo [ERROR] No se encontro pythonw.exe. Ejecuta instalar.bat primero.
    pause & exit /b 1
)

REM Lanzar GUI sin ninguna consola
start "" "%PYWEXE%" "%~dp0src\txt2media\ui\ventana_principal.py"
