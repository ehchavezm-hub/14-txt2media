@echo off
REM diagnostico_gui.bat — Muestra errores sin cerrarse
cd /d "%~dp0"
echo =========================================
echo  txt2media — Diagnostico GUI
echo =========================================
echo.

REM Verificar Python
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "%PYCMD%"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "%PYCMD%"=="" (
    echo [ERROR] Python no encontrado.
    pause & exit /b 1
)
echo [OK] Python: %PYCMD%

REM Verificar PySide6
echo.
echo [1] Verificando PySide6...
%PYCMD% -c "import PySide6; print('PySide6', PySide6.__version__)"
if errorlevel 1 (
    echo [ERROR] PySide6 NO instalado. Instalando ahora...
    %PYCMD% -m pip install "PySide6>=6.10.0"
    if errorlevel 1 ( echo [ERROR] No se pudo instalar PySide6. & pause & exit /b 1 )
)

REM Verificar modulo txt2media
echo.
echo [2] Verificando modulo txt2media...
%PYCMD% -c "import txt2media; print('txt2media', txt2media.__version__)"
if errorlevel 1 (
    echo [ERROR] txt2media no instalado. Instalando...
    %PYCMD% -m pip install -e .
    if errorlevel 1 ( echo [ERROR] pip install fallo. & pause & exit /b 1 )
)

REM Intentar abrir GUI directamente
echo.
echo [3] Abriendo GUI...
%PYCMD% -m txt2media.ui.ventana_principal
if errorlevel 1 (
    echo [ERROR] La GUI fallo. Ver mensaje arriba.
    pause & exit /b 1
)
pause
