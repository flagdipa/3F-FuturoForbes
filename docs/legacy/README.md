# FuturoForbes - Sistema de Gestión Financiera Personal

Sistema moderno de gestión financiera personal desarrollado con FastAPI y AdminLTE4.

## Características

- 🏦 Gestión de múltiples cuentas bancarias
- 💰 Registro de transacciones (ingresos/gastos/transferencias)
- 📊 Presupuestos y seguimiento
- 📈 Reportes y gráficos interactivos
- 🔄 Sistema de reglas automáticas
- 💱 Soporte multi-divisa
- 🎯 Metas de ahorro
- 📱 Responsive (funciona en móvil y desktop)

## Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno
- **SQLModel** - ORM con type hints
- **PostgreSQL** - Base de datos
- **Alembic** - Migraciones
- **JWT** - Autenticación

### Frontend
- **AdminLTE 4** - Dashboard template
- **Chart.js** - Gráficos
- **DataTables** - Tablas interactivas
- **Alpine.js** - Interactividad

## Quick Start

### 1. Configurar entorno virtual

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configurar base de datos

```bash
cp .env.template .env
# Editar .env con tus credenciales
```

### 3. Ejecutar migraciones

```bash
alembic upgrade head
```

### 4. Iniciar servidor

```bash
uvicorn main:app --reload
```

Abrir: http://localhost:8000

## Estructura del Proyecto

```
futuroForbes/
├── backend/              # API FastAPI
│   ├── api/             # Endpoints
│   ├── core/            # Configuración
│   ├── models/          # Modelos
│   ├── schemas/         # Schemas
│   └── main.py
├── frontend/            # AdminLTE4
│   ├── assets/
│   ├── pages/
│   └── index.html
└── docs/                # Documentación
```

## Licencia

MIT
