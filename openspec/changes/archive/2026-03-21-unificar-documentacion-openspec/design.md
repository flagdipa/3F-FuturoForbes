## Context

El proyecto 3F (Futuro Forbes) es un sistema de gestión financiera personal con aproximadamente 25,000 líneas de código Python, 8,000 líneas de JavaScript, y múltiples documentos dispersos que describen el sistema:

- `SUMMARY_SISTEMA_TOTAL.md` - Visión consolidada de arquitectura y estado
- `INFORME_RELEVAMIENTO_3F.md` - Informe técnico detallado (1,342 líneas)
- `ARQUITECTURA_DEFINITIVA.md` - Decisiones arquitectónicas y diagramas
- `PROMPT_PLUGINS.md` - Especificaciones del sistema de plugins
- Documentos legado en `docs/legacy/` (5 archivos)

**Estado actual:**
- Backend: FastAPI con 28 routers API, 30+ modelos SQLModel
- Frontend: 22 templates HTML con Alpine.js
- Plugins: 13 plugins funcionales
- Testing: Pytest + Playwright
- Despliegue: Docker + Windows (.bat)

## Goals / Non-Goals

**Goals:**
- Consolidar toda la documentación dispersa en OpenSpec como fuente única de verdad
- Documentar cada capacidad/módulo con especificaciones claras y testables
- Establecer base para futuras implementaciones y modificaciones
- Crear inventario completo de plugins, modelos y endpoints
- Preparar especificaciones para versiones futuras (v2.1, v3.0)

**Non-Goals:**
- No modificar código existente del sistema
- No implementar nuevas funcionalidades (solo documentar existentes)
- No migrar datos de base de datos
- No crear tests automatizados (solo especificaciones)

## Decisions

### 1. Estructura de Specs
**Decisión:** Crear 14 especificaciones separadas, una por cada capacidad identificada.
**Rationale:** Cada capacidad (core financiero, plugins, IA, etc.) tiene alcance independiente y puede evolucionar separadamente.
**Alternativas consideradas:**
- Un solo spec monolítico → Rechazado por dificultad de mantenimiento
- Agrupar specs relacionadas → Rechazado, cada módulo merece su propia documentación

### 2. Prioridad de Documentación
**Decisión:** Ordenar specs por criticidad: core-financiero → sistema-plugins → gestion-avanzada → IA/reportes
**Rationale:** El core financiero es la base de todo; sin él, otros módulos no funcionan.

### 3. Nivel de Detalle
**Decisión:** Documentar requerimientos a nivel funcional (qué hace) no técnico (cómo implementa)
**Rationale:** OpenSpec specs deben ser independientes de la implementación específica.

### 4. Manejo de Plugins
**Decisión:** Crear spec específica para arquitectura de plugins + specs individuales para plugins complejos
**Rationale:** La arquitectura de plugins es crítica; cada plugin importante merece su propia especificación.

### 5. Conservación de Documentos Legado
**Decisión:** Mantener documentos originales en `docs/legacy/` mientras se migra a OpenSpec
**Rationale:** Referencia histórica y posible necesidad de rollback.

## Risks / Trade-offs

### [Riesgo] Documentación queda obsoleta rápidamente
**Mitigación:** Establecer proceso de actualización de specs al mismo tiempo que el código. Usar OpenSpec para trackear cambios futuros.

### [Riesgo] Complejidad de 14 specs diferentes
**Mitigación:** Documentar primero las 5 specs críticas, luego las restantes en iteraciones posteriores.

### [Riesgo] Inconsistencias entre documentos originales y specs
**Mitigación:** Revisar código fuente actual para validar specs, no solo confiar en documentos existentes.

### [Trade-off] Tiempo vs. Cobertura
Documentar todo lleva tiempo significativo. Se priorizará:
1. Core financiero (cuentas, transacciones)
2. Sistema de plugins
3. Funcionalidades restantes

## Migration Plan

### Fase 1: Specs Críticas (Semana 1)
1. core-financiero (cuentas, transacciones, categorías)
2. sistema-plugins (arquitectura y base)
3. seguridad-auditoria (auth, JWT, logs)

### Fase 2: Gestión Avanzada (Semana 2)
4. gestion-presupuestos
5. metas-ahorro
6. activos-inversiones
7. transacciones-recurrentes

### Fase 3: Features Especiales (Semana 3)
8. inteligencia-artificial
9. reportes-analisis
10. boveda-digital
11. multi-moneda

### Fase 4: UX y Misc (Semana 4)
12. temas-customizacion
13. importacion-exportacion
14. notificaciones-multi

## Open Questions

1. **¿Se documentan plugins individuales como specs separadas?** 
   - Respuesta: Plugins complejos (criptoya_multi, backup_automatico) sí; plugins simples (telegram_bot) en spec general.

2. **¿Qué tan detallados deben ser los escenarios?**
   - Respuesta: Suficientes para que un tester pueda validar sin ver el código.

3. **¿Se incluyen errores/edge cases en scenarios?**
   - Respuesta: Sí, escenarios de error son obligatorios para requerimientos críticos.

## Referencias

- Archivos fuente analizados: `SUMMARY_SISTEMA_TOTAL.md`, `INFORME_RELEVAMIENTO_3F.md`, `ARQUITECTURA_DEFINITIVA.md`, `PROMPT_PLUGINS.md`
- Plugins existentes: `backend/plugins/` (13 plugins)
- Modelos: `backend/models/` (30+ archivos)
- API: `backend/api/` (28 routers)
