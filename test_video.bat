@echo off
cd /d "%~dp0"
set PYCMD=
py -3.14 --version >nul 2>&1 && set PYCMD=py -3.14
if "%PYCMD%"=="" py -3.13 --version >nul 2>&1 && set PYCMD=py -3.13
if "%PYCMD%"=="" ( echo Python no encontrado. & pause & exit /b 1 )

echo === TEST VIDEO txt2media ===
echo.
echo ffmpeg:
where ffmpeg 2>&1
echo.

%PYCMD% "%~dp0_test_video.py"
echo.
echo Codigo de salida: %errorlevel%
pause
