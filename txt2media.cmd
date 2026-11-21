@echo off
REM ============================================================================
REM  txt2media.cmd - Usar txt2media desde la terminal (CMD o PowerShell)
REM
REM  Antes de cada uso trae la ultima version desde GitHub (git pull) y, si
REM  cambiaron las dependencias, las reinstala.
REM
REM  Uso (desde la carpeta del repositorio, p. ej. D:\PST\txt2media):
REM    txt2media                     Abre la ventana
REM    txt2media convertir libro.pdf --formato audio
REM    txt2media convertir a.pdf b.epub --formato video --salida D:\Salida
REM    txt2media info                Estado del sistema (ffmpeg, voces, claves)
REM    txt2media actualizar          Solo git pull + dependencias
REM    txt2media ayuda               Lista de comandos y opciones
REM
REM  Para saltarse el git pull una vez:   set TXT2MEDIA_SIN_PULL=1
REM ============================================================================
setlocal
set "RAIZ=%~dp0"
if "%RAIZ:~-1%"=="\" set "RAIZ=%RAIZ:~0,-1%"

REM ---- 1. Python -------------------------------------------------------------
set "PY="
py -3.13 --version >nul 2>&1 && set "PY=py -3.13"
if not defined PY py -3.12 --version >nul 2>&1 && set "PY=py -3.12"
if not defined PY python --version >nul 2>&1 && set "PY=python"
if not defined PY (
    echo [ERROR] No se encontro Python 3.12 o 3.13.
    echo         Instalalo desde https://www.python.org/downloads/ y marca "Add Python to PATH".
    exit /b 1
)

REM ---- 2. git pull -----------------------------------------------------------
set "REINSTALAR="
if defined TXT2MEDIA_SIN_PULL goto :Dependencias
git --version >nul 2>&1 || (
    echo [AVISO] Git no esta instalado: se usa la version local sin actualizar.
    goto :Dependencias
)
if not exist "%RAIZ%\.git" goto :Conectar
set "ANTES="
for /f %%h in ('git -C "%RAIZ%" rev-parse HEAD') do set "ANTES=%%h"
echo [git] Actualizando desde GitHub...
git -C "%RAIZ%" pull --ff-only
if errorlevel 1 (
    echo [AVISO] git pull no se pudo completar ^(sin conexion o cambios locales^).
    echo         Se continua con la version local.
    goto :Dependencias
)
git -C "%RAIZ%" diff --quiet %ANTES% HEAD -- pyproject.toml || set "REINSTALAR=1"
goto :Dependencias

:Conectar
REM Carpeta descomprimida de un ZIP: se conecta con GitHub una sola vez.
echo [git] Esta carpeta no esta conectada a GitHub. Conectando...
git -C "%RAIZ%" init -q
git -C "%RAIZ%" remote add origin https://github.com/ehchavezm-hub/14-txt2media.git
git -C "%RAIZ%" fetch -q origin main
if errorlevel 1 (
    echo [AVISO] No se pudo descargar desde GitHub. Se usa la version local.
    rmdir /s /q "%RAIZ%\.git"
    goto :Dependencias
)
git -C "%RAIZ%" symbolic-ref HEAD refs/heads/main
git -C "%RAIZ%" reset -q --hard origin/main
git -C "%RAIZ%" branch -q --set-upstream-to=origin/main main
echo [git] Listo: esta carpeta ya se actualiza desde GitHub.
set "REINSTALAR=1"

:Dependencias
REM ---- 3. Dependencias (solo si faltan o cambio pyproject.toml) ---------------
%PY% -c "import txt2media, PySide6, pdfplumber, edge_tts" >nul 2>&1 || set "REINSTALAR=1"
if defined REINSTALAR (
    echo [pip] Instalando dependencias...
    %PY% -m pip install -e "%RAIZ%" --no-build-isolation -q --no-warn-script-location
    if errorlevel 1 %PY% -m pip install -e "%RAIZ%" -q --no-warn-script-location
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias. Revisa el mensaje de pip arriba.
        exit /b 1
    )
)

REM ---- 4. Ejecutar -----------------------------------------------------------
if "%~1"=="" goto :Ventana
if /i "%~1"=="gui" goto :Ventana
if /i "%~1"=="actualizar" (
    echo [OK] txt2media actualizado.
    exit /b 0
)
if /i "%~1"=="ayuda" (
    %PY% -m txt2media.cli.main --help
    exit /b %errorlevel%
)
%PY% -m txt2media.cli.main %*
exit /b %errorlevel%

:Ventana
echo [txt2media] Abriendo la ventana... ^(cierra la ventana para volver a la terminal^)
%PY% -m txt2media.ui.ventana_principal
if errorlevel 1 (
    echo [ERROR] La ventana se cerro con un error. El detalle esta arriba.
    exit /b 1
)
exit /b 0
