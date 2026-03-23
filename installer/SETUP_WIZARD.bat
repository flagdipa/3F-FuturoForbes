@echo off
setlocal enabledelayedexpansion
title Configurando 3F FuturoForbes

echo.
echo  ============================================================
1: echo     CONFIGURACION POST-INSTALACION DE 3F
echo  ============================================================
echo.

cd /d "%~dp0"

:: 1. Verificar Python
echo [1/4] Verificando Python...
set PYTHON_CMD=
for %%P in (python py python3) do (
    if not defined PYTHON_CMD (
        %%P --version >nul 2>&1
        if !errorlevel! equ 0 set PYTHON_CMD=%%P
    )
)

if not defined PYTHON_CMD (
    echo [ERROR] No se pudo encontrar Python en el sistema.
    echo Por favor, instala Python 3.10 o superior desde python.org
    pause
    exit /b 1
)

:: 2. Crear Entorno Virtual
echo [2/4] Creando entorno virtual local aislado...
if not exist ".venv" (
    %PYTHON_CMD% -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)
echo [OK] Entorno virtual listo.

:: 3. Instalar Dependencias
echo [3/4] Instalando paquetes necesarios (esto puede tardar unos minutos)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r backend\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar dependencias. Verifique su conexion a internet.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: 4. Inicializar Datos
echo [4/4] Inicializando configuracion y base de datos...
if not exist ".env" (
    python -c "import secrets; key=secrets.token_hex(32); f=open('.env','w'); f.write(f'DATABASE_URL=sqlite:///3f_app.db\nSECRET_KEY={key}\nPORT=8000\nHOST=127.0.0.1\nDEBUG_MODE=False\n'); f.close()"
)

set PYTHONPATH=%CD%
python -c "from backend.core.database import init_db; init_db();"
echo [OK] Base de datos inicializada.

echo.
echo ============================================================
echo  INSTALACION FINALIZADA CON EXITO
echo ============================================================
echo.
echo Puedes iniciar el sistema desde el acceso directo del escritorio.
echo.
timeout /t 5
