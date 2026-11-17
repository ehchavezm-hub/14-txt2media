@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: ---------------------------------------------------------------
:: AUTO-ELEVACION: pide permiso de administrador automaticamente
:: El usuario solo hace clic en "Si" en el cuadro de Windows
:: ---------------------------------------------------------------
net session >nul 2>&1
if errorlevel 1 (
    powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

:: ---------------------------------------------------------------
:: VENTANA GRANDE Y LIMPIA
:: ---------------------------------------------------------------
mode con cols=60 lines=25
color 0A
title  txt2media -- Instalando...

cls
echo.
echo   ===================================================
echo    txt2media v1.0.1
echo    Instalacion automatica
echo   ===================================================
echo.
echo    Por favor espera, esto toma 1-2 minutos...
echo.

:: ---------------------------------------------------------------
:: PASO 1: VERIFICAR SI PYTHON YA ESTA INSTALADO
:: ---------------------------------------------------------------
call :DetectarPython
if not "!PYCMD!"=="" goto :TenemosPython

:: ---------------------------------------------------------------
:: PASO 2: INSTALAR PYTHON CON WINGET (automatico)
:: ---------------------------------------------------------------
echo    Instalando Python...

winget --version >nul 2>&1
if errorlevel 1 goto :SinWinget

:: Detectar S Mode
set SMODE=0
for /f "tokens=3" %%a in ('reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\CI\Policy" /v "SkuPolicyRequired" 2^>nul') do set SMODE=%%a

if "!SMODE!"=="0x1" (
    :: S Mode: instalar Python desde la Microsoft Store (unica opcion valida en S Mode)
    winget install --id 9PJPW5LDXLZ5 --source msstore --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
) else (
    :: Normal: instalar Python 3.13
    winget install --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    if errorlevel 1 (
        winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    )
)

:: Recargar el PATH de Windows para encontrar Python recien instalado
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "PATH=!PATH!;%%b"

call :DetectarPython
if "!PYCMD!"=="" goto :ErrorPython
goto :TenemosPython

:SinWinget
:: Sin winget: descargar Python directamente
echo    Descargando instalador de Python...
set PYURL=https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe
set PYINST=%TEMP%\python_setup.exe
powershell -NoProfile -Command "Invoke-WebRequest -Uri '!PYURL!' -OutFile '!PYINST!'" >nul 2>&1
if exist "!PYINST!" (
    echo    Instalando Python (esto puede tardar un momento)...
    "!PYINST!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "PATH=%%b"
    call :DetectarPython
)
if "!PYCMD!"=="" goto :ErrorPython

:: ---------------------------------------------------------------
:: PASO 3: INSTALAR txt2media
:: ---------------------------------------------------------------
:TenemosPython
echo    Instalando txt2media...
!PYCMD! -m pip install -e . -q --no-warn-script-location >nul 2>&1
if errorlevel 1 (
    !PYCMD! -m pip install -e . --no-warn-script-location >nul 2>&1
    if errorlevel 1 goto :ErrorPip
)

:: ---------------------------------------------------------------
:: PASO 4: CREAR ACCESO DIRECTO EN EL ESCRITORIO
:: ---------------------------------------------------------------
echo    Creando acceso directo...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\txt2media.lnk
set LAUNCHERPYW=%~dp0lanzar.pyw
set ICONPATH=%~dp0assets\icon.ico

for /f "delims=" %%p in ('where pythonw 2^>nul') do if "!PYTHONW!"=="" set PYTHONW=%%p
if "!PYTHONW!"=="" (
    for /f "delims=" %%p in ('where python 2^>nul') do if "!PYTHONW!"=="" set PYTHONW=%%p
)

if not exist "!ICONPATH!" set ICONPATH=%SystemRoot%\System32\imageres.dll,11

powershell -NoProfile -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('!SHORTCUT!');^
   $s.TargetPath='!PYTHONW!';^
   $s.Arguments='\"!LAUNCHERPYW!\"';^
   $s.WorkingDirectory='%~dp0';^
   $s.IconLocation='!ICONPATH!';^
   $s.Description='txt2media v1.0.1';^
   $s.Save()" >nul 2>&1

:: ---------------------------------------------------------------
:: LISTO
:: ---------------------------------------------------------------
cls
color 0A
echo.
echo   ===================================================
echo.
echo       INSTALACION COMPLETADA
echo.
echo       Para usar txt2media:
echo       Busca el icono "txt2media" en tu Escritorio
echo       y haz doble clic.
echo.
echo   ===================================================
echo.
echo   Esta ventana se cerrara en 10 segundos...
timeout /t 10 >nul
exit /b 0

:: ---------------------------------------------------------------
:: MENSAJES DE ERROR (simples, sin tecnicismos)
:: ---------------------------------------------------------------
:ErrorPython
cls
color 0C
echo.
echo   ===================================================
echo    No se pudo instalar Python automaticamente.
echo.
echo    Contacta a soporte tecnico.
echo    (Error: Python no encontrado)
echo   ===================================================
echo.
timeout /t 15 >nul
exit /b 1

:ErrorPip
cls
color 0C
echo.
echo   ===================================================
echo    Error de conexion a Internet.
echo.
echo    Verifica el Internet y vuelve a abrir este archivo.
echo   ===================================================
echo.
timeout /t 15 >nul
exit /b 1

:: ---------------------------------------------------------------
:: FUNCION: detectar Python disponible
:: ---------------------------------------------------------------
:DetectarPython
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14 & goto :eof
py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13 & goto :eof
py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12 & goto :eof
py -3.11 --version >nul 2>&1 && set PYCMD=py -3.11 & goto :eof
python --version >nul 2>&1 && set PYCMD=python & goto :eof
goto :eof
