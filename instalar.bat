@echo off
REM instalar.bat — Configura el proyecto en una laptop nueva
cd /d "%~dp0"
echo =============================================
echo  txt2media v1.0.1 — Instalacion en laptop
echo =============================================

REM Verificar Python
where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado.
    echo Descarga Python 3.13 desde https://python.org
    pause & exit /b 1
)
echo [OK] Python encontrado.

REM Configurar git
git config user.email "ehchavezm@cosapi.com.pe"
git config user.name "COSAPI txt2media"
echo [OK] Git configurado.

REM Instalar dependencias
echo Instalando dependencias Python...
py -3.13 -m pip install -e . -q
echo [OK] Dependencias instaladas.

REM Verificar instalacion
py -3.13 -m txt2media.cli.main --version
echo.
echo =============================================
echo  Listo. Usa guardar.bat para hacer backup.
echo =============================================
pause
