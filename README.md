# 3F FuturoForbes — Sistema de Gestión Financiera Personal

**Versión:** 2.0.0 — Stable Build  
**Fecha:** Marzo 2026

---

## 🚀 Inicio Rápido

### Primera vez (Instalación)
```
Doble click en → INSTALAR.bat
```

### Uso diario (Arrancar el servidor)
```
Doble click en → INICIAR.bat
```

Luego abre el navegador en: **http://localhost:8000**

---

## 📋 Requisitos

- **Python** 3.10 o superior  
  👉 [Descargar Python](https://www.python.org/downloads/)
- **Windows** 10/11 (para los .bat)
- Conexión a internet (solo en la primera instalación, para descargar dependencias)

---

## 🗂️ Estructura del Proyecto

```
3F/
├── INSTALAR.bat         # ← Instalador (ejecutar primera vez)
├── INICIAR.bat          # ← Arrancar servidor (uso diario)
├── .env                 # Configuración local (NO subir a git)
├── .env.example         # Plantilla de configuración
├── backend/             # API FastAPI (Python)
│   ├── main.py          # Punto de entrada
│   ├── api/             # Endpoints REST
│   │   ├── v1/          # Rutas API V2 (cuentas, transacciones, etc.)
│   │   └── auth/        # Autenticación JWT
│   ├── core/            # Servicios del núcleo (ledger, IA, plugins)
│   └── models/          # Modelos de base de datos (SQLModel)
├── frontend/            # Interfaz Web (HTML + Alpine.js)
│   ├── static/js/       # JavaScript de la aplicación
│   └── templates/       # Plantillas HTML
└── scripts/             # Scripts auxiliares y seeds
```

---

## ⚙️ Configuración

Copia `.env.example` como `.env` y ajusta los valores:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de la base de datos | `sqlite:///3f_app.db` |
| `SECRET_KEY` | Clave secreta para JWT | (generada automáticamente) |
| `PORT` | Puerto del servidor | `8000` |
| `DEBUG_MODE` | Modo debug | `False` |

---

## 🛠️ Comandos de Desarrollo

Activar el entorno virtual primero:
```powershell
.\.venv\Scripts\activate
```

| Tarea | Comando |
|-------|---------|
| Iniciar servidor (dev) | `python -m uvicorn backend.main:app --reload` |
| Ejecutar tests | `pytest backend/tests/` |
| Reiniciar DB | Elimina `3f_app.db` y reinicia |

---

## 📊 Estado del Sistema

| Módulo | Estado |
|--------|--------|
| Autenticación (JWT) | ✅ Funcional |
| Cuentas (Accounts) | ✅ Funcional |
| Transacciones (Double-Entry) | ✅ Funcional |
| Categorías | ✅ Funcional |
| Beneficiarios (Payees) | ✅ Funcional |
| Presupuestos | 🔧 En desarrollo |
| Metas de Ahorro | 🔧 En desarrollo |
| Inversiones | 🔧 En desarrollo |
| Plugins | 🔧 En desarrollo |
| IA / OCR | 🔧 En desarrollo |

---

## 🐛 Reporte de Bugs

Los errores conocidos están documentados en `estado_proyecto.md`.

---

## 📝 Licencia

Proyecto privado — © 2026 FuturoForbes
