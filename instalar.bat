@echo off
REM instalar.bat — Configura TODO automáticamente. Ejecutar UNA SOLA VEZ.
cd /d "%~dp0"
set REPO=%~dp0

echo =============================================
echo  txt2media — Configuracion automatica
echo =============================================

REM 1. Verificar Python
where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado.
    echo Descarga Python 3.13 desde https://python.org y vuelve a ejecutar.
    pause & exit /b 1
)
echo [OK] Python encontrado.

REM 2. Configurar git
git config user.email "ehchavezm@cosapi.com.pe"
git config user.name "COSAPI txt2media"
git config credential.helper manager
echo [OK] Git configurado.

REM 3. Instalar dependencias Python
echo Instalando dependencias...
py -3.13 -m pip install -e . -q
echo [OK] Dependencias instaladas.

REM 4. Crear tarea programada: auto-guardar en GitHub cada 5 minutos (silencioso)
schtasks /delete /tn "txt2media-autosave" /f >nul 2>&1
schtasks /create ^
  /tn "txt2media-autosave" ^
  /tr "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File \"%REPO%auto_guardar.ps1\"" ^
  /sc minute /mo 5 ^
  /ru "%USERNAME%" ^
  /f >nul 2>&1
if errorlevel 1 (
    echo [WARN] No se pudo crear la tarea automatica. Ejecuta como Administrador.
) else (
    echo [OK] Auto-guardado cada 5 minutos activado.
)

REM 5. Verificar instalacion
echo.
py -3.13 -m txt2media.cli.main --version
echo.
echo =============================================
echo  TODO LISTO. No necesitas hacer nada mas.
echo  GitHub se actualiza solo cada 5 minutos.
echo =============================================
pause
