@echo off
REM guardar.bat — Guarda todo en GitHub con un doble clic
cd /d "%~dp0"
echo Guardando en GitHub...
git add -A
git diff --cached --quiet >nul 2>&1
if errorlevel 1 (
    for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set FECHA=%%c-%%b-%%a
    git commit -m "auto: guardado %FECHA%"
    git push origin main
    echo.
    echo [OK] Cambios guardados en GitHub.
) else (
    echo [OK] Sin cambios nuevos.
)
timeout /t 3 >nul
