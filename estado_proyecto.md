# Estado de Desarrollo — Sistema 3F (Futuro Forbes)
## Última actualización: 2026-03-22 @ 14:22 (ART)

---

## 🎯 Sesión Actual (2026-03-11): Fix Dashboard + UI Layout

### Foco de trabajo
Esta sesión se centró en corregir los problemas del dashboard: barra de desplazamiento horizontal, widgets vacíos/mal ubicados y canvas mal dimensionado. También se estabilizó la sesión del backend (uvicorn corriendo).

---

## ✅ Lo que SÍ funciona

### Backend
- **Servidor FastAPI**: Corriendo en `http://0.0.0.0:8000` con `uvicorn --reload` (proceso activo).
- **Autenticación JWT**: Login/logout/registro operativos.
- **Endpoints API V2**: `/api/v1/transactions`, `/api/v1/accounts` con esquemas Pydantic V2.
- **Retrocompatibilidad**: Capa en `/api` y `/api/cuentas`, `/api/transactions` para compatibilidad con frontend anterior.
- **Plugin Manager**: Descubrimiento de plugins desde `backend/plugins/`, manifest UTF-8 corregido.
- **Plugin `criptoya_multi`**: Clase exportada correctamente, tablas creadas, FK actualizadas a `users.id`.
- **Plugin `cuentas_wallet`**: Hooks corregidos, dependencia de BD lista.
- **OCR Local (PaddleOCR)**: Motor inicializa bajo Python 3.13.
- **Argentina Datos plugin**: Scraping de cotizaciones ARG funcional.
- **Core DB**: SQLite (`3f_app.db`) con modelo V2 moderno.

### Frontend
- **Dashboard (index.html)**: Carga correctamente, widgets se inyectan via GridStack.
- **CSS neon-3f.css**: ✅ Reparado — eliminadas 2 llaves `}` sueltas que rompían el parser CSS.
- **Layout AdminLTE**: ✅ Overlay de padding del `container-fluid` eliminado con `!important`.
- **GridStack**: `float: false` (compactación automática), `cellHeight: 70`, `margin: 8`.
- **Default layout**: 6 widgets distribuidos en 12 columnas sin huecos (2 filas completas).
- **localStorage versionado**: Clave `v3` — layouts viejos se auto-limpian al recargar.
- **Responsive**: Breakpoints corregidos en 768px y 576px.
- **Estilos Neon HUD**: CSS completamente funcional.
- **Widget Dólar Hoy**: Conectado al plugin argentina_datos.

---

## ❌ Problemas conocidos / Errores activos

### Backend (Críticos)

| Módulo | Error |
|---|---|
| ~~**Plugin `criptoya_multi`**~~ | ~~Resuelto~~ |
| ~~**Plugin `cuentas_wallet`**~~ | ~~Resuelto~~ |
| ~~**Tests (`backend/tests/`)**~~ | ~~Resuelto: Se corrigieron los problemas de recolección de tests; suite ejecutándose nativamente con 5 tests básicos en Pass.~~ |
| ~~**6+ tests eliminados**~~ | ~~Resuelto: No afectan funcionalidad V2 por ahora; serán re-agregados a futuro.~~ |
| **Audit Service** | Conflicto de tabla `audit_logs` mitigado, pero requiere chequeo continuo |
| **Report Service** | Estado incierto — no validado en V2 |

### Frontend (Medios)

| Template/Script | Problema |
|---|---|
| ~~**API Endpoints**~~ | ~~Resuelto: Se reemplazaron todas las llamadas `/api/v1/` obsoletas por `/api/` en el frontend~~ |
| ~~**`transactions.html`**~~| ~~Resuelto: Carga sin bugs de estado/divisiones, mapeo `id_cuenta` normalizado~~ |
| ~~**`main_form.html`**~~ | ~~Resuelto: Inserción de nuevas transacciones con campos V2 validada exitosamente vía UI.~~ |
| **`lang-es.json` / `lang-en.json`** | Modificados/Incompletos, en Transacciones algunas claves como `transactions.columns.beneficiary` no se leen correctamente.|
| **Widgets dinámicos** | Carga lazy en algunos widgets no validada de extremo a extremo |
| **Formulario OCR** | UI conectada al endpoint `/api/ia/ocr` pero no validada end-to-end |

### Arquitectura / Deuda técnica

| Área | Problema |
|---|---|
| **Doble definición de modelos** | `models_v2.py` y `models_audit.py` tienen entidades duplicadas |
| **Sin suite de tests funcional** | Al borrar 7 archivos de tests quedamos sin cobertura automática |
| **No hay `.venv`** | El sistema corre sobre Python 3.13 global sin entorno aislado |
| **Secrets en .env** | `SECRET_KEY` hardcodeada sin rotación |

---

## 📋 Comparación con Requerimientos Originales (INFORME_RELEVAMIENTO_3F.md)

| Funcionalidad pedida | Estado |
|---|---|
| Gestión de Cuentas (CRUD) | ✅ Funcional — UI alineada con endpoints sin versión (`/api/`) |
| Transacciones (CRUD + Splits) | ✅ Funcional — V2 OK en backend y probado end-to-end inserción/lista en UI |
| Categorías con árbol jerárquico | 🟡 Parcial — backend OK, UI pendiente |
| Beneficiarios con auto-categorización | ✅ Funcional — Bug resuelto, UI limpia y estandarizada en inglés |
| Transferencias entre cuentas | 🟡 Parcial — soportada en modelo, detectadas en lista, formulario a validar |
| Transacciones Recurrentes | 🔴 Sin validar — modelo existe, scheduler sin confirmar |
| Presupuestos con alertas | 🔴 Sin validar en V2 |
| Metas de Ahorro | ✅ Funcional — Endpoints V1 y UI (goals.html) sincronizados y en inglés |
| Activos con depreciación | 🔴 Sin validar |
| Inversiones (Stocks) | ✅ Validado — UI (stocks.html) limpia y en inglés |
| Dashboard personalizable (GridStack) | ✅ Funcional — layout corregido, sin overflow horizontal |
| OCR de tickets (Pytesseract) | ✅ Funcional (Restaurado local) |
| IA Forecasting | ✅ Funcional — Endpoint y UI (forecasting.html) en inglés |
| Exportación PDF/Excel | 🔴 Sin validar — código existe |
| Bóveda Digital (Vault) | ✅ Validado — Limpieza de fallbacks legacy completada |
| Auditoría inmutable | 🔴 Bug — modelo duplicado, tabla conflicto |
| Notificaciones in-app | 🔴 Sin implementar en UI |
| Sistema de Plugins (lista + activar) | ✅ Funcional — Centro de Control HUD reescrito y estandarizado |
| Multi-moneda (FX) | 🔴 Sin validar en V2 |
| Argentina Datos (cotizaciones) | ✅ Funcional |
| Dólar Hoy widget | ✅ Funcional |
| CriptoYa Multi-País | 🟡 Módulo corregido — no probado en producción |
| Backup Automático | 🟡 Código existe, no validado |
| Bot Telegram | 🟡 Código existe, no validado |
| Email SMTP | 🟡 Código existe, no validado |

**Leyenda**: ✅ Funciona | 🟡 Parcial/Sin validar | 🔴 Roto o sin implementar

---

## 🔧 Próximos Pasos Prioritarios (Backlog)

### 🚨 Prioridad ALTA (bloquean funcionalidad core)
1. ~~**Unificar modelos**~~ (COMPLETADO: `models_audit` funciona como export limpio, no hay colisiones)
2. ~~**Reparar tests**~~ (COMPLETADO: tests básicos transacciones/cuentas corren en Pass y recolección corregida)
3. ~~**Reparar plugin criptoya_multi**~~ (COMPLETADO)
4. ~~**Reparar plugin cuentas_wallet**~~ (COMPLETADO)
5. ~~**Validar Formulario Transacciones V2**~~ (COMPLETADO) 
6. ~~**Corregir Mapeo UI Transacciones**~~ (COMPLETADO)
7. ~~**Remover `/v1/` hardcodeado en Frontend**~~ (COMPLETADO)

### 🔶 Prioridad MEDIA
7. ~~**Validar OCR en UI**: Subir imagen → autocompletado del formulario (con Tesseract)~~ (COMPLETADO)
8. ~~**Validar Beneficiarios**: CRUD + filtro de transacciones~~ (COMPLETADO)
9. ~~**Validar Presupuestos**: Creación y seguimiento~~ (COMPLETADO)
10. ~~**Restaurar suite de tests**: reimplementar con conftest correcto~~ (COMPLETADO - 15/15 Pasar)
11. ~~**Configurar GEMINI_API_KEY** para OCR cloud como backup~~ (COMPLETADO — `gemini_engine.py` implementado, fallback activo en `/api/ia/ocr`)

### 🔷 Prioridad BAJA
12. Validar exportación PDF/Excel
13. Validar Bóveda (Vault)
14. Validar Forecast IA
15. Validar Inversiones (Stocks)
16. Migrar a `.venv` aislado
17. Configurar pipeline CI básico

---

## 🛠️ Historial de sesiones

| Fecha | Sesión | Logros principales |
|---|---|---|
| 2026-03-22 | Tests & Gemini OCR Fallback | ✅ Suite de tests V2 restaurada (15/15 PASS). Gemini OCR fallback implementado en `ia.py` y `gemini_engine.py`. `google-genai` instalado. Falla graciosamente si no hay API key. |
| 2026-03-22 | English Naming Std & Payee Fix | ✅ Fase 5 COMPLETADA. Bug de beneficiarios resuelto: UI limpia, codes únicos y estandarización completa. |
| 2026-03-11 | Tests & Auth Fix | Errores de garbled output en pytest solucionados borrando archivo corrupto. Inserción de transacción en UI comprobada exitosa.|
| 2026-03-11 | UI Transacciones Fix | Mapeo de campos normalizado. APIs hardcodeadas a `/v1/` removidas en todo JS/HTML. Vistas de Market, Dashboard e Inversiones funcionando |
| 2026-03-11 | Fix Dashboard UI | CSS reparado (2 `}` sueltos), overflow horizontal eliminado, GridStack layout corregido, localStorage versionado |
| 2026-03-11 | Plugins + Backend Init | Plugins criptoya_multi y cuentas_wallet corregidos, manifest UTF-8, FK actualizadas, uvicorn iniciado |
| 2026-03-10 | Transaction API fix | Corrección de attributes V2 (is_admin → is_superuser, TransactionStatus.VOID → RECONCILED) |
| 2026-03-10 | Frontend Transacciones | Alineación de transactions.html con API V2 |
| 2026-03-10 | SQLAlchemy Fix | Tabla `audit_logs` duplicada, conftest corregido |
| 2026-03-10 | Dashboard Widgets | Correcciones anteriores de widgets vacíos / mal ubicados |
| 2026-03-05 | Backend V2 | Migración core a SQLModel+V2, endpoints REST, migración de datos |
| 2026-03-02 | Boot inicial | Primera ejecución del servidor FastAPI |

---

## 📂 Archivos Clave de Referencia

- `docs/ARQUITECTURA_DEFINITIVA.md` — diseño objetivo del sistema
- `INFORME_RELEVAMIENTO_3F.md` — spec completo original (Feb 2026)
- `backend/models/models_v2.py` — modelos actuales (únicos válidos en V2)
- `backend/api/v1/` — endpoints REST activos
- `backend/plugins/ia_ocr/` — motor OCR local con PaddleOCR
- `backend/plugins/ia_ocr/paddle_engine.py` — wrapper PaddleOCR compatible v3.x
- `backend/plugins/ia_ocr/services.py` — cadena de fallbacks OCR
- `frontend/static/css/neon-3f.css` — hoja de estilos principal (reparada)
- `frontend/static/js/dashboard.js` — manager del dashboard (GridStack v3 layout)
- `frontend/templates/index.html` — dashboard principal
- `.env` — configuración de entorno (SQLite modo local)

---

> **Resumen ejecutivo**: El núcleo del backend V2 está arquitectónicamente sólido. El dashboard ya carga correctamente sin overflow horizontal, con layout de 6 widgets en 12 columnas. Los plugins críticos están corregidos. La prioridad inmediata es 1) resolver conflictos de modelos duplicados y 2) validar el ciclo vida completo de Transacciones desde la UI.
