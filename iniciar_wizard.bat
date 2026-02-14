@echo off
cls
echo ====================================
echo  WIZARD DE INSTALACION FUTUROFORBES 3F
echo ====================================
echo.
echo El wizard ahora esta integrado en el sistema principal.
echo.
echo Iniciando servidor en el puerto 8000...
echo.
echo Accede a:
echo   http://localhost:8000/install
echo.
echo IMPORTANTE:
echo  - Este script inicia el sistema COMPLETO en modo instalacion.
echo  - No necesitas el puerto 8080.
echo.
pause
echo.
echo Iniciando...
cd /d "%~dp0"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
