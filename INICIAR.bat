@echo off
setlocal
title 3F FuturoForbes - Servidor

echo.
echo  ============================================================
echo     3F FUTUROFORBES - Iniciando Servidor v2.1
echo  ============================================================
echo.

:: -------------------------------------------------------
:: Detectar el entorno virtual disponible
:: -------------------------------------------------------
set PYTHON_EXE=
set VENV_FOUND=0

if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    set VENV_FOUND=1
) else if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
    set VENV_FOUND=1
) else if exist "..\.venv\Scripts\python.exe" (
    set PYTHON_EXE=..\.venv\Scripts\python.exe
    set VENV_FOUND=1
) else if exist "..\venv\Scripts\python.exe" (
    set PYTHON_EXE=..\venv\Scripts\python.exe
    set VENV_FOUND=1
)

if %VENV_FOUND%==0 (
    echo [ERROR] No se encontro entorno virtual. Ejecuta INSTALAR.bat primero.
    pause
    exit /b 1
)

if not exist .env (
    echo [ERROR] Archivo .env no encontrado. Ejecuta INSTALAR.bat primero.
    pause
    exit /b 1
)

echo [OK] Entorno virtual detectado.
echo [INFO] Iniciando servidor en http://localhost:8000
echo [INFO] Presiona Ctrl+C para detener el servidor.
echo.

set PYTHONPATH=%CD%
start "" "http://localhost:8000"

%PYTHON_EXE% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
