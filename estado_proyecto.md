# Estado de Desarrollo — Sistema 3F (Futuro Forbes)
## Última actualización: 2026-03-10

---

## 🎯 Sesión Actual (2026-03-10): Refactor V2 + Estabilización

### Foco de trabajo
Esta sesión se centró en la migración del API/modelos al esquema V2, estabilización del frontend para usar esos endpoints, y la integración del motor OCR local con PaddleOCR. El sistema tiene aún **errores significativos** en varios módulos.

---

## ✅ Lo que SÍ funciona

### Backend
- **Servidor FastAPI**: Arranca correctamente con `py -3.13` vía `iniciar_sistema.bat` en SQLite.
- **Autenticación JWT**: Login/logout/registro operativos.
- **Endpoints API V2**: `/api/v1/transactions`, `/api/v1/accounts` con esquemas Pydantic V2.
- **Retrocompatibilidad**: Capa en `/api` y `/api/cuentas`, `/api/transactions` para compatibilidad con frontend anterior.
- **Plugin Manager**: Descubrimiento de plugins desde `backend/plugins/`.
- **OCR Local (PaddleOCR)**: Motor inicializa correctamente bajo Python 3.13 con flags `enable_mkldnn=False, use_tensorrt=False`. Extrae texto en modo sync vía hilo. Parseo de texto a estructura financiera con regex.
- **EasyOCR**: Instalado como alternativa (aunque el usuario prefiere PaddleOCR).
- **Core DB**: SQLite (`3f_app.db`) con modelo V2 moderno.
- **Argentina Datos plugin**: Scraping de cotizaciones ARG funcional.

### Frontend
- **Dashboard (index.html)**: Carga base, widgets se inyectan.
- **Formulario de Transacciones**: Estructura con Alpine.js presente.
- **Estilos Neon HUD**: CSS activo.
- **Widget Dólar Hoy**: Conectado al plugin argentina_datos.

---

## ❌ Problemas conocidos / Errores activos

### Backend (Críticos)

| Módulo | Error |
|---|---|
| **Plugin `criptoya_multi`** | `AttributeError: 'module' object has no attribute 'CriptoyaMultiPlugin'` — la clase no exporta nombre correcto |
| **Plugin `cuentas_wallet`** | Error al cargar hooks, dependencia interna rota |
| **Tests (`backend/tests/`)** | `sqlalchemy.exc.InvalidRequestError: Table 'plugins' already defined` — múltiples definiciones de `AuditLog` entre `models_audit.py` y `models_v2.py` |
| **6+ tests eliminados** | `test_accounts_api.py`, `test_base_crud.py`, `test_beneficiaries_api.py`, `test_csv_parser.py`, `test_plugins.py`, `test_plugins_api.py`, `test_reconciliation.py` — borrados como parte de limpieza, sin reemplazo |
| **Audit Service** | Posibles conflictos de tabla `audit_logs` entre dos definiciones de modelo |
| **Report Service** | Estado incierto — no validado en V2 |

### Frontend (Medios)

| Template/Script | Problema |
|---|---|
| **`transactions.html`** | Pendiente alineación completa con V2 (campos renombrados en esquema) |
| **`main_form.html`** | Formulario de transacción puede no mapear bien todos los campos V2 |
| **`lang-en.json`** | Modificado, puede tener claves faltantes o redundantes |
| **Widgets dinámicos** | Carga lazy en algunos widgets no validada de extremo a extremo |
| **Formulario OCR** | UI conectada al endpoint `/api/v1/ia/ocr` pero no validada visualmente end-to-end |

### Arquitectura / Deuda técnica

| Área | Problema |
|---|---|
| **Doble definición de modelos** | `models_v2.py` y `models_audit.py` tienen entidades duplicadas. Resolver con modelos únicos. |
| **Sin suite de tests funcional** | Al borrar 7 archivos de tests quedamos sin cobertura automática |
| **Logging de LOG roto** | `app.log` muestra entradas antiguas (Feb 2026) mezcladas con nuevas (Mar 2026) |
| **No hay `.venv`** | El sistema corre sobre la instalación global de Python 3.13 sin entorno aislado |
| **Secrets en .env** | La `SECRET_KEY` está hardcodeada en `.env` sin rotación |

---

## 📋 Comparación con Requerimientos Originales (INFORME_RELEVAMIENTO_3F.md)

| Funcionalidad pedida | Estado |
|---|---|
| Gestión de Cuentas (CRUD) | 🟡 Parcial — V2 implementado, frontend no 100% alineado |
| Transacciones (CRUD + Splits) | 🟡 Parcial — V2 OK en backend, UI en ajuste |
| Categorías con árbol jerárquico | 🟡 Parcial — backend OK, UI pendiente |
| Beneficiarios con auto-categorización | 🔴 Con bug — `beneficiary-manager.js` modificado pero no validado |
| Transferencias entre cuentas | 🟡 Parcial — soportada en modelo, UI sin validar |
| Transacciones Recurrentes | 🔴 Sin validar — modelo existe, scheduler sin confirmar |
| Presupuestos con alertas | 🔴 Sin validar en V2 |
| Metas de Ahorro | 🟡 Parcial — endpoints existen, UI sin probar |
| Activos con depreciación | 🔴 Sin validar |
| Inversiones (Stocks) | 🔴 Sin validar en V2 |
| Dashboard personalizable (GridStack) | 🟡 Activo pero widgets con datos mock/fallbacks |
| OCR de tickets (PaddleOCR) | 🟡 Local funciona — UI no validada end-to-end |
| IA Forecasting | 🔴 Sin validar — endpoint existe pero no probado |
| Exportación PDF/Excel | 🔴 Sin validar — código existe |
| Bóveda Digital (Vault) | 🔴 Sin validar |
| Auditoría inmutable | 🔴 Bug — modelo duplicado, tabla conflicto |
| Notificaciones in-app | 🔴 Sin implementar en UI |
| Sistema de Plugins (lista + activar) | 🟡 Parcial — descubrimiento OK, 2 plugins con errores |
| Multi-moneda (FX) | 🔴 Sin validar en V2 |
| Argentina Datos (cotizaciones) | ✅ Funcional |
| Dólar Hoy widget | ✅ Funcional |
| CriptoYa Multi-País | 🔴 Bug al cargar módulo |
| Backup Automático | 🟡 Código existe, no validado |
| Bot Telegram | 🟡 Código existe, no validado |
| Email SMTP | 🟡 Código existe, no validado |

**Leyenda**: ✅ Funciona | 🟡 Parcial/Sin validar | 🔴 Roto o sin implementar

---

## 🔧 Próximos Pasos Prioritarios (Backlog)

### 🚨 Prioridad ALTA (bloquean funcionalidad core)
1. **Unificar modelos**: Eliminar duplicado de `AuditLog` — un solo modelo en un solo archivo
2. **Reparar tests**: Recrear suite básica para transactions + accounts en V2
3. **Reparar plugin criptoya_multi**: Exportar clase correctamente
4. **Reparar plugin cuentas_wallet**: Diagnosticar fallo de hooks
5. **Validar Transacciones V2 end-to-end**: Crear, editar, eliminar desde UI

### 🔶 Prioridad MEDIA
6. **Validar OCR en UI**: Subir imagen → autocompletado del formulario
7. **Validar Beneficiarios**: CRUD + filtro de transacciones
8. **Validar Presupuestos**: Creación y seguimiento
9. **Restaurar suite de tests**: reimplementar con conftest correcto
10. **Configurar GEMINI_API_KEY** para OCR cloud como backup

### 🔷 Prioridad BAJA
11. Validar exportación PDF/Excel
12. Validar Bóveda (Vault)
13. Validar Forecast IA
14. Validar Inversiones (Stocks)
15. Migrar a `.venv` aislado
16. Configurar pipeline CI básico

---

## 📂 Archivos Clave de Referencia

- `docs/ARQUITECTURA_DEFINITIVA.md` — diseño objetivo del sistema
- `INFORME_RELEVAMIENTO_3F.md` — spec completo original (Feb 2026)
- `backend/models/models_v2.py` — modelos actuales (únicos válidos en V2)
- `backend/api/v1/` — endpoints REST activos
- `backend/plugins/ia_ocr/` — motor OCR local con PaddleOCR
- `backend/plugins/ia_ocr/paddle_engine.py` — wrapper PaddleOCR compatible v3.x
- `backend/plugins/ia_ocr/services.py` — cadena de fallbacks OCR
- `.env` — configuración de entorno (SQLite modo local)

---

> **Resumen ejecutivo**: El núcleo del backend V2 está arquitectónicamente sólido pero con múltiples módulos sin validar y algunos rotos. El frontend está mayoritariamente en transición al V2. La prioridad inmediata es estabilizar el ciclo vida completo de Transacciones + resolver los conflictos de modelos duplicados.
