@echo off
:: build_exe.bat — Genera txt2media.exe portable (sin instalacion, sin admin)
:: Requisito: Python 3.12+ instalado
cd /d "%~dp0..\.."

echo.
echo  ===================================================
echo   Generando txt2media.exe (esto toma ~5 minutos)
echo  ===================================================
echo.

:: Instalar dependencias
echo  [1/3] Instalando dependencias...
python -m pip install -e . -q
python -m pip install pyinstaller -q
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause & exit /b 1
)

:: Compilar EXE
echo  [2/3] Compilando EXE...
set ICON_OPT=
if exist "assets\icon.ico" set ICON_OPT=--icon=assets\icon.ico

python -m PyInstaller ^
  --onefile ^
  --noconsole ^
  --name txt2media ^
  --collect-all PySide6 ^
  --collect-all edge_tts ^
  --hidden-import pyttsx3 ^
  --hidden-import keyring.backends.Windows ^
  --hidden-import langdetect ^
  %ICON_OPT% ^
  herramientas\compilar\main_exe.py

if not exist "dist\txt2media.exe" (
    echo [ERROR] No se genero el EXE. Revisa los mensajes de error arriba.
    pause & exit /b 1
)

echo  [3/3] Listo.
echo.
echo  ===================================================
echo   EXE generado: dist\txt2media.exe
echo   Ese archivo abre txt2media con doble clic.
echo   Sin instalar, sin Python, sin admin.
echo  ===================================================
echo.
explorer dist
pause
