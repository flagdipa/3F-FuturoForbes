## Context

Acabamos de finalizar y archivar la Fase 1 correspondiente al core financiero de 3F guiándonos por las 1342 líneas del `INFORME_RELEVAMIENTO_3F.md`. La arquitectura de extracción ("Escalpelo Vertical") demostró ser eficiente para aislar contexto y evitar saturación en la redacción de specs.

## Goals / Non-Goals

**Goals:**
- Mapear las 4 capacidades definidas como "Fase 2: Gestión Avanzada" en el plan maestro original.
- Extender el paradigma de lectura rápida vertical al resto de documentos de la arquitectura 3F.

**Non-Goals:**
- Implementar IA o reportes (eso quedará para Fase 3).
- Escribir código fuente.

## Decisions

### 1. Reutilización de Táctica (Escalpelo Vertical)
**Decisión:** Aplicaremos exactamente la misma estrategia de "leer solo las secciones requeridas" del INFORME base para cada spec de esta fase.
**Rationale:** Evita errores, contexto mezclado y mantiene el estándar de calidad conseguido en la Fase 1.

### 2. Separación de Presupuestos del Core Financiero
**Decisión:** Aunque los presupuestos afectan al core, tendrán una spec exclusiva (`gestion-presupuestos.md`).
**Rationale:** Su motor de cálculo de excedentes (`alert_threshold`) y rolling period amerita un tratamiento individual.

## Migration Plan / Execution

1. Generar **gestion-presupuestos**: Extraer sec 4.1.5, 5.1.6 y API `/budgets`
2. Generar **metas-ahorro**: Extraer sec 4.2.3, 5.1.8 y API `/goals`
3. Generar **activos-inversiones**: Extraer sec 4.2.1, 4.2.2, 5.1.7 y API `/assets` - `/stocks`
4. Generar **transacciones-recurrentes**: Extraer sec 4.2.5, 5.1.3 y servicios internos paralelos.
