@echo off
:: build_exe.bat — Genera txt2media_setup.exe en la carpeta dist\
:: Requisito: Python 3.13 instalado (ejecuta instalar_universal.bat primero)
cd /d "%~dp0"

echo.
echo  Generando txt2media_setup.exe...
echo.

:: Instalar PyInstaller
python -m pip install pyinstaller -q
if errorlevel 1 (
    echo [ERROR] No se pudo instalar PyInstaller.
    pause & exit /b 1
)

:: Inyectar ZIP en bootstrap_installer.py y compilar
python -c "
import zipfile, base64, pathlib, os, io

files = ['instalar_universal.bat','lanzar.pyw','crear_acceso.py','txt2media_gui.bat','pyproject.toml']
if os.path.exists('assets/icon.ico'):
    files.append('assets/icon.ico')
for p in pathlib.Path('src').rglob('*.py'):
    files.append(str(p).replace(chr(92), '/'))

buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    [z.write(f, 'txt2media/'+f) for f in files if os.path.exists(f)]

b64 = base64.b64encode(buf.getvalue()).decode()
with open('bootstrap_installer.py', encoding='utf-8') as fh:
    code = fh.read()
code = code.replace('\"__ZIP_CONTENT__\"', '\"\"\"' + b64 + '\"\"\"', 1)
with open('bootstrap_filled.py', 'w', encoding='utf-8') as fh:
    fh.write(code)
print('ZIP inyectado OK:', len(b64)//1024, 'KB')
"

if errorlevel 1 (
    echo [ERROR] No se pudo preparar el bootstrap.
    pause & exit /b 1
)

:: Detectar icono
set ICON_OPT=
if exist "assets\icon.ico" set ICON_OPT=--icon=assets\icon.ico

:: Compilar EXE
pyinstaller --onefile --noconsole --name txt2media_setup %ICON_OPT% bootstrap_filled.py
del bootstrap_filled.py >nul 2>&1

if exist "dist\txt2media_setup.exe" (
    echo.
    echo  ===================================================
    echo   EXE listo: dist\txt2media_setup.exe
    echo   Puedes compartir ese archivo directamente.
    echo  ===================================================
    echo.
    explorer dist
) else (
    echo [ERROR] No se genero el EXE.
    pause & exit /b 1
)
pause
