@echo off
REM construir_portable.bat — Genera dist\txt2media\ portable para Windows
REM Ejecutar desde la carpeta raiz del proyecto como Administrador
cd /d "%~dp0..\.."

echo =============================================
echo  txt2media v1.0.1 — Construir version portable
echo =============================================

REM Detectar Python
REM Preferir 3.14 y 3.13 — Pillow aun no soporta 3.15
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "%PYCMD%"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "%PYCMD%"=="" py -3.12 --version >nul 2>&1 && set PYCMD=py -3.12
if "%PYCMD%"=="" py -3.15 --version >nul 2>&1 && set PYCMD=py -3.15
if "%PYCMD%"=="" (
    echo [ERROR] Python no encontrado.
    pause & exit /b 1
)
echo [OK] Usando: %PYCMD%

REM Instalar dependencias del proyecto
echo.
echo [1/4] Instalando dependencias...
%PYCMD% -m pip install -e . -q
if errorlevel 1 ( echo [ERROR] pip install fallo. & pause & exit /b 1 )

REM Instalar PyInstaller
echo [2/4] Instalando PyInstaller...
%PYCMD% -m pip install "pyinstaller>=6.5.0" -q
if errorlevel 1 ( echo [ERROR] No se pudo instalar PyInstaller. & pause & exit /b 1 )
echo [OK] PyInstaller listo.

REM Limpiar build anterior
echo [3/4] Limpiando build anterior...
if exist "dist\txt2media" rmdir /s /q "dist\txt2media"
if exist "build" rmdir /s /q "build"

REM Construir
echo [4/4] Construyendo ejecutable portable...
echo     (puede tardar 2-5 minutos)
%PYCMD% -m PyInstaller herramientas\compilar\txt2media.spec --noconfirm --clean
if errorlevel 1 (
    echo [ERROR] PyInstaller fallo. Ver mensajes arriba.
    pause & exit /b 1
)

REM Crear lanzador amigable
echo @echo off > "dist\txt2media\convertir.bat"
echo REM Uso: arrastra un archivo sobre este .bat o edita la linea de abajo >> "dist\txt2media\convertir.bat"
echo set ARCHIVO=%%1 >> "dist\txt2media\convertir.bat"
echo if "%%ARCHIVO%%"=="" set /p ARCHIVO="Ruta del archivo a convertir: " >> "dist\txt2media\convertir.bat"
echo. >> "dist\txt2media\convertir.bat"
echo echo Formato: pptx, docx, xlsx, audio, video >> "dist\txt2media\convertir.bat"
echo set /p FORMATO="Formato de salida [pptx]: " >> "dist\txt2media\convertir.bat"
echo if "%%FORMATO%%"=="" set FORMATO=pptx >> "dist\txt2media\convertir.bat"
echo. >> "dist\txt2media\convertir.bat"
echo txt2media.exe convertir "%%ARCHIVO%%" --formato %%FORMATO%% >> "dist\txt2media\convertir.bat"
echo pause >> "dist\txt2media\convertir.bat"

REM Crear ZIP portable
echo.
echo Creando ZIP portable...
%PYCMD% -c "import shutil; shutil.make_archive('dist/txt2media_v1.0.1_portable_win64', 'zip', 'dist', 'txt2media')"
echo.
echo =============================================
echo  LISTO
echo  Carpeta: dist\txt2media\
echo  ZIP:     dist\txt2media_v1.0.1_portable_win64.zip
echo.
echo  Para usar sin instalar nada:
echo    dist\txt2media\txt2media.exe info
echo    dist\txt2media\txt2media.exe convertir archivo.pdf --formato pptx
echo =============================================
pause
