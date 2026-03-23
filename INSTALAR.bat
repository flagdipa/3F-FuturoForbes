@echo off
setlocal enabledelayedexpansion
title 3F FuturoForbes - Instalador

echo.
echo  ============================================================
echo     3F FUTUROFORBES - Instalador de Sistema Local v2.1
echo  ============================================================
echo.

:: -------------------------------------------------------
:: 1. Detectar Python instalado
:: -------------------------------------------------------
set PYTHON_CMD=
for %%P in (python py python3) do (
    if not defined PYTHON_CMD (
        %%P --version >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_CMD=%%P
        )
    )
)

if not defined PYTHON_CMD (
    echo [ERROR] Python no encontrado. Instala Python 3.10+ desde:
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%V in ('%PYTHON_CMD% --version 2^>^&1') do set PY_VER=%%V
echo [OK] Python encontrado: %PY_VER%

:: -------------------------------------------------------
:: 2. Buscar el entorno virtual (en el proyecto o uno nivel arriba)
:: -------------------------------------------------------
set VENV_PATH=
if exist ".venv\Scripts\python.exe" (
    set VENV_PATH=.venv
    echo [OK] Entorno virtual encontrado en .venv\
) else if exist "venv\Scripts\python.exe" (
    set VENV_PATH=venv
    echo [OK] Entorno virtual encontrado en venv\
) else if exist "..\venv\Scripts\python.exe" (
    set VENV_PATH=..\venv  
    echo [OK] Entorno virtual encontrado en ..\venv\    
) else if exist "..\.venv\Scripts\python.exe" (
    set VENV_PATH=..\.venv
    echo [OK] Entorno virtual encontrado en ..\.venv\
) else (
    echo [INFO] Creando entorno virtual en .venv\...
    %PYTHON_CMD% -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    set VENV_PATH=.venv
    echo [OK] Entorno virtual creado.
)

:: -------------------------------------------------------
:: 3. Instalar dependencias
:: -------------------------------------------------------
echo [INFO] Activando entorno e instalando dependencias...
call %VENV_PATH%\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r backend\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Fallo instalar dependencias. Revisa backend\requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: -------------------------------------------------------
:: 4. Crear .env si no existe
:: -------------------------------------------------------
if not exist .env (
    echo [INFO] Generando .env con configuracion por defecto...
    python -c "import secrets; key=secrets.token_hex(32); f=open('.env','w'); f.write(f'DATABASE_URL=sqlite:///3f_app.db\nSECRET_KEY={key}\nPORT=8000\nHOST=0.0.0.0\nDEBUG_MODE=False\n'); f.close()"
    echo [OK] Archivo .env creado.
) else (
    echo [OK] .env ya existe, manteniendo configuracion.
)

:: -------------------------------------------------------
:: 5. Inicializar base de datos
:: -------------------------------------------------------
echo [INFO] Inicializando base de datos...
set PYTHONPATH=%CD%
python -c "from backend.core.database import init_db; init_db(); print('[OK] Base de datos lista.')"

:: -------------------------------------------------------
:: 6. Guardar ruta del venv para el INICIAR.bat
:: -------------------------------------------------------
echo %VENV_PATH% > .venv_path

echo.
echo  ============================================================
echo   [OK] Instalacion completada!
echo   Ejecuta INICIAR.bat para arrancar el sistema.
echo  ============================================================
echo.

set /p ARRANCAR="Deseas iniciar el sistema ahora? (S/N): "
if /i "%ARRANCAR%"=="S" (
    start "" "http://localhost:8000"
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
)

pause
