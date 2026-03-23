## Why

El proyecto 3F (Futuro Forbes) cuenta con múltiples documentos dispersos (.md) que describen la arquitectura, funcionalidades, plugins y especificaciones del sistema. Esta fragmentación dificulta el mantenimiento, la implementación de nuevas features y la incorporación de nuevos desarrolladores. Es necesario consolidar toda esta información en OpenSpec para establecer una única fuente de verdad que facilite la evolución futura del sistema.

## What Changes

- **Consolidación documental**: Unificar todos los archivos .md existentes en el ecosistema OpenSpec
- **Creación de especificaciones centrales**: Generar specs para cada módulo y capacidad del sistema
- **Estandarización de requerimientos**: Documentar de forma estructurada todas las funcionalidades actuales y planificadas
- **Preparación para futuras implementaciones**: Establecer base sólida para próximas modificaciones e implementaciones
- **Inventario completo**: Documentar todos los plugins existentes (13 plugins activos), modelos de datos (30+) y endpoints API (28 routers)

## Capabilities

### New Capabilities
<!-- Capabilities del Sistema 3F que se documentarán en specs -->
- `core-financiero`: Gestión de cuentas, transacciones, categorías y beneficiarios con motor de doble entrada
- `gestion-presupuestos`: Sistema de presupuestos mensuales/anuales con alertas y seguimiento
- `metas-ahorro`: Definición y seguimiento de metas de ahorro con progreso visual
- `activos-inversiones`: Control de activos físicos (depreciación) e inversiones (stocks, ETFs, cripto)
- `reportes-analisis`: Dashboard personalizable, reportes estándar y avanzados, exportación PDF/Excel
- `inteligencia-artificial`: OCR de tickets con Gemini, forecasting de gastos, sugerencias de categorización
- `sistema-plugins`: Arquitectura extensible con 13 plugins funcionales (telegram, email, criptoya, backup, etc.)
- `seguridad-auditoria`: JWT authentication, rate limiting, logs de auditoría inmutables
- `multi-moneda`: Soporte multi-divisa con tasas de cambio en tiempo real
- `boveda-digital`: Almacenamiento seguro de documentos importantes
- `transacciones-recurrentes**: Automatización de pagos programados
- `temas-customizacion`: Sistema de temas (Dark, Light, Cyberpunk) con personalización UI
- `importacion-exportacion**: Migración desde MMEX, exportación múltiples formatos
- `notificaciones-multi**: Email, Telegram, in-app alerts

### Modified Capabilities
<!-- No hay capacidades existentes en OpenSpec para modificar -->
- *Ninguna - primera documentación en OpenSpec*

## Impact

- **Backend**: FastAPI + SQLModel + SQLite/MySQL/PostgreSQL
- **Frontend**: Alpine.js + Bootstrap + AdminLTE con temas Neon/Cyberpunk
- **API**: 28 routers REST con ~150+ endpoints
- **Base de datos**: 30+ modelos SQL con relaciones complejas
- **Plugins**: 13 plugins funcionales en backend/plugins/
- **Testing**: Pytest (backend) + Playwright (frontend)
- **Despliegue**: Docker + Docker Compose + Windows (.bat)
- **Documentación**: Unificación de 5+ archivos .md principales + legado

---

**Contexto del Proyecto:**
- **Nombre**: 3F (Futuro Forbes)
- **Versión**: 2.0.0 Stable
- **Estado**: Producción Ready
- **Stack**: Python 3.11+, FastAPI 0.128, SQLModel 0.0.31, Alpine.js 3.13, Bootstrap 5.3
- **Influencias**: MoneyManagerEX, Firefly III, GnuCash, PrestaShop (arquitectura plugins)
- **Principios**: Double-entry accounting, soft delete, Decimal precision, inmutable audit logs
