@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    INSTALADOR LOCAL - FUTUROFORBES 3F   
echo ==========================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado. Descargalo de https://www.python.org/
    pause
    exit /b 1
)

:: 2. Crear Entorno Virtual
if not exist .venv (
    echo [INFO] Creando entorno virtual...
    python -m venv .venv
)

:: 3. Instalar dependencias
echo [INFO] Instalando dependencias (esto puede tardar unos minutos)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

:: 4. Lanzar
echo.
echo [OK] Entorno preparado con exito.
echo [INFO] Abriendo el navegador en el asistente de instalacion...
start http://localhost:8000/install
echo.
echo Presiona Ctrl+C para cerrar el servidor una vez finalizada la instalacion.
echo.

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
