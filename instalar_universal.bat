@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo  =========================================================
echo   txt2media v1.0.1 -- Instalador Universal
echo   Funciona en Windows 10/11, 32-bit, 64-bit y ARM
echo  =========================================================
echo.

:: ---------------------------------------------------------------
:: 1. DETECTAR WINDOWS S MODE
::    S Mode bloquea todos los EXE que no vienen de la Store.
::    La solucion: salir de S Mode (gratis) o usar este .bat + Python.
:: ---------------------------------------------------------------
set SMODE=0
for /f "tokens=3" %%a in ('reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\CI\Policy" /v "SkuPolicyRequired" 2^>nul') do set SMODE=%%a
if "!SMODE!"=="0x1" (
    echo [!] WINDOWS S MODE DETECTADO
    echo.
    echo     Tu equipo tiene Windows S Mode, que solo permite apps
    echo     de la Microsoft Store. Los archivos .exe no funcionan.
    echo.
    echo     SOLUCION GRATUITA ^(1 minuto^):
    echo       1. Inicio -^> Configuracion -^> Sistema -^> Activacion
    echo       2. Clic en "Cambiar a Windows 10/11 Home" (o Pro/etc.)
    echo       3. Confirma en la Store ^(es gratis, irreversible^)
    echo       4. Reinicia y vuelve a ejecutar este archivo
    echo.
    echo     Mientras tanto, si tienes Python instalado:
    echo       Doble clic en  lanzar.pyw  en esta carpeta.
    echo.
    pause & exit /b 0
)
echo [OK] Windows S Mode: no activo.

:: ---------------------------------------------------------------
:: 2. VERIFICAR / INSTALAR PYTHON
:: ---------------------------------------------------------------
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "!PYCMD!"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "!PYCMD!"=="" py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12
if "!PYCMD!"=="" py -3.11 --version >nul 2>&1 && set PYCMD=py -3.11

if "!PYCMD!"=="" (
    echo [!] Python no encontrado. Intentando instalar automaticamente...
    echo.

    :: Intentar con winget (disponible en Windows 10 1809+ y Windows 11)
    winget --version >nul 2>&1
    if not errorlevel 1 (
        echo     Instalando Python 3.13 con winget...
        winget install -e --id Python.Python.3.13 --silent --accept-package-agreements --accept-source-agreements
        if not errorlevel 1 (
            echo [OK] Python 3.13 instalado.
            :: Recargar PATH
            call refreshenv >nul 2>&1
            py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
        )
    )

    if "!PYCMD!"=="" (
        echo.
        echo [ERROR] No se pudo instalar Python automaticamente.
        echo.
        echo  INSTALA PYTHON MANUALMENTE:
        echo    1. Ve a: https://www.python.org/downloads/
        echo    2. Descarga Python 3.13 (elige 32-bit si tu PC es 32-bit)
        echo    3. Durante la instalacion, marca "Add Python to PATH"
        echo    4. Vuelve a ejecutar este archivo
        echo.
        pause & exit /b 1
    )
)
echo [OK] Python detectado: !PYCMD!

:: ---------------------------------------------------------------
:: 3. INSTALAR DEPENDENCIAS txt2media
:: ---------------------------------------------------------------
echo.
echo Instalando txt2media y sus dependencias...
!PYCMD! -m pip install -e . -q
if errorlevel 1 (
    echo [ERROR] Fallo al instalar dependencias.
    echo Verifica tu conexion a Internet y vuelve a intentarlo.
    pause & exit /b 1
)
echo [OK] txt2media instalado.

:: ---------------------------------------------------------------
:: 4. CONFIGURAR GIT (opcional, para desarrollo)
:: ---------------------------------------------------------------
git --version >nul 2>&1
if not errorlevel 1 (
    git config user.email "ehchavezm@cosapi.com.pe" >nul 2>&1
    git config user.name "COSAPI txt2media" >nul 2>&1
    echo [OK] Git configurado.
)

:: ---------------------------------------------------------------
:: 5. CREAR ACCESO DIRECTO EN EL ESCRITORIO
::    Apunta a lanzar.pyw con pythonw (sin consola DOS)
:: ---------------------------------------------------------------
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\txt2media.lnk
set TARGET=%~dp0lanzar.pyw

:: Detectar pythonw correspondiente a la version detectada
for /f "tokens=2 delims=-" %%v in ("!PYCMD!") do set PYVER=%%v
for /f "delims=" %%p in ('where pythonw 2^>nul') do set PYTHONW=%%p
if "!PYTHONW!"=="" (
    for /f "delims=" %%p in ('where python 2^>nul') do set PYTHONW=%%p
)

powershell -NoProfile -Command ^
 "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('!SHORTCUT!');^
  $s.TargetPath='!PYTHONW!';^
  $s.Arguments='\"!TARGET!\"';^
  $s.WorkingDirectory='%~dp0';^
  $s.IconLocation='%~dp0assets\icon.ico,0';^
  $s.Description='txt2media v1.0.1';^
  $s.Save()" >nul 2>&1

if exist "!SHORTCUT!" (
    echo [OK] Acceso directo creado en el Escritorio.
) else (
    echo [WARN] No se pudo crear el acceso directo. Usa lanzar.pyw directamente.
)

:: ---------------------------------------------------------------
:: 6. VERIFICACION FINAL
:: ---------------------------------------------------------------
echo.
!PYCMD! -m txt2media.cli.main --version
echo.
echo  =========================================================
echo   LISTO. Para abrir txt2media:
echo     - Doble clic en "txt2media" en el Escritorio, O
echo     - Doble clic en  lanzar.pyw  en esta carpeta
echo   (No necesitas el archivo .exe)
echo  =========================================================
echo.
pause
