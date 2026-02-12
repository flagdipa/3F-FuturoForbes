@echo off
setlocal
cd /d "c:\xampp\htdocs\3F"

echo ==========================================
echo 🚀 Iniciando FuturoForbes (3F) Backend
echo 📂 Directorio: %CD%
echo ==========================================

:: Configurar PYTHONPATH para que reconozca el modulo 'backend'
set PYTHONPATH=c:\xampp\htdocs\3F

:: Iniciar servidor FastAPI con Uvicorn
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
