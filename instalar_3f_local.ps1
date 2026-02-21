# Script de Instalación Local para FuturoForbes 3F
# Este script prepara el entorno y lanza el asistente de instalación

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   INSTALADOR LOCAL - FUTUROFORBES 3F   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python no está instalado. Por favor, instálalo desde python.org" -ForegroundColor Red
    pause
    exit
}

# 2. Crear Entorno Virtual si no existe
if (!(Test-Path ".venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

# 3. Activar y actualizar pip
Write-Host "🚀 Actualizando pip e instalando dependencias..." -ForegroundColor Yellow
& ".\.venv\Scripts\pip.exe" install --upgrade pip
& ".\.venv\Scripts\pip.exe" install -r backend/requirements.txt

# 4. Lanzar el Asistente de Instalación
Write-Host ""
Write-Host "✅ Entorno preparado." -ForegroundColor Green
Write-Host "🌐 Lanzando asistente en http://localhost:8000/install" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para cerrar una vez terminada la instalación." -ForegroundColor Gray
Write-Host ""

# Ejecutar el wizard desde backend/main.py
# El backend detecta si no está instalado y redirige / a /install o carga el modulo de install
$env:PORT = "8080"
& ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --port 8000 --reload
