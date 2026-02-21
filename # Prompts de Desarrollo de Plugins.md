# Prompts de Desarrollo de Plugins — Sistema 3F

---

# 🔌 PROMPT 1 — Plugin: Argentina Datos (Información Financiera)

---

## Contexto del Sistema

Eres un desarrollador senior del sistema **3F**. Tu tarea es **planificar e implementar** un módulo plugin de información financiera para este sistema. Debes seguir estrictamente los **skills, convenciones y estructura de plugins** establecidos en el proyecto 3F.

---

## Objetivo

Crear un plugin llamado **"Argentina Datos"** que consuma las APIs públicas de [argentinadatos.com](https://argentinadatos.com) para mostrar información financiera actualizada dentro del sistema 3F.

---

## Recursos Disponibles

| Recurso | Ubicación / URL |
|---|---|
| Servidor API | `https://api.argentinadatos.com` |
| Documentación online | `https://argentinadatos.com/docs/` |
| Repositorio GitHub de APIs | `https://github.com/flagdipa/esjs-argentina-datos` |
| Ejemplo de datos JSON | `\finanzas personales\argentinadatos_api.json` |
| Ejemplo de datos YAML | `\finanzas personales\argentinadatos_api.yaml` |

> ⚠️ **Antes de comenzar**, leer y analizar los archivos `.json`, `.yaml` y explorar el repositorio GitHub `flagdipa/esjs-argentina-datos`. El acceso al repositorio está disponible desde **Antigravity**.

---

## Estructura del Repositorio (referencia)

El repositorio `flagdipa/esjs-argentina-datos` está organizado de la siguiente manera. Esta estructura es la fuente de verdad para entender qué datos están disponibles y cómo se organizan los endpoints:

```
esjs-argentina-datos/
├── api/
│   └── api.esjs                          ← Servidor Hono. Registra rutas dinámicas desde /datos
├── src/
│   ├── cotizaciones/
│   │   ├── cotizaciones.cron.esjs        ← Extrae y guarda cotizaciones y dólares
│   │   └── extraccion/
│   │       ├── extraerCotizaciones.esjs
│   │       └── extraerDolares.esjs
│   └── finanzas/
│       ├── finanzas.cron.esjs            ← Orquesta todos los extractores de finanzas
│       ├── extraccion/                   ← Extractores: inflación, plazo fijo, tasas, UVA, etc.
│       ├── fci/
│       ├── rendimientos/
│       ├── riesgoPais/
│       ├── criptopesos/
│       ├── cuentas-remuneradas-usd/
│       ├── hipotecariosUva/
│       ├── creditosHipotecariosUva/
│       └── inflacionREM/
└── datos/
    └── v1/
        ├── cotizaciones/
        │   ├── index.json                ← Cotizaciones actuales (todas las divisas)
        │   ├── dolares/
        │   │   ├── index.json            ← Historial completo dólares (2011–2026)
        │   │   ├── blue/                 ← Dólar blue histórico
        │   │   ├── oficial/              ← Dólar oficial histórico
        │   │   ├── bolsa/                ← Dólar bolsa (MEP) histórico
        │   │   ├── contadoconliqui/      ← CCL histórico
        │   │   ├── cripto/               ← Dólar cripto histórico
        │   │   ├── mayorista/            ← Dólar mayorista histórico
        │   │   ├── solidario/            ← Dólar solidario histórico
        │   │   ├── tarjeta/              ← Dólar tarjeta histórico
        │   │   └── [2011..2026]/         ← Datos históricos por año
        │   ├── [2023..2026]/             ← Cotizaciones generales históricas por año
        │   └── usd/, eur/, brl/, clp/, uyu/  ← Cotizaciones por divisa
        └── finanzas/
            ├── inflacion/                ← Inflación mensual e interanual
            ├── tasas/
            │   ├── plazoFijo/            ← Tasa de plazo fijo actual
            │   ├── plazosFijos/          ← Tasas de plazos fijos por entidad
            │   └── depositos30Dias/      ← Tasas de depósitos a 30 días
            ├── indices/                  ← Índice UVA
            ├── fci/                      ← Fondos comunes de inversión
            ├── rendimientos/             ← Rendimientos
            ├── creditos/                 ← Créditos hipotecarios UVA
            ├── hipotecarios-uva/         ← TNA hipotecarios UVA
            ├── criptopesos/              ← Cotización criptopesos (Belo)
            └── cuentas-remuneradas-usd/  ← Cuentas remuneradas en USD
```

> 💡 El servidor API (`api/api.esjs`) registra dinámicamente todas las rutas basándose en la estructura de carpetas de `/datos`. Cada carpeta con un `index.json` se convierte en un endpoint accesible en `https://api.argentinadatos.com/v1/...`.

---

## Alcance de APIs a Consumir

Solo se implementarán los siguientes grupos de endpoints:

### 1. Cotizaciones Actuales
- `GET /v1/cotizaciones` — Cotización actual de todas las divisas
- `GET /v1/cotizaciones/usd` — Dólar (tipos: oficial, blue, bolsa, ccl, cripto, mayorista, solidario, tarjeta)
- `GET /v1/cotizaciones/eur` — Euro
- `GET /v1/cotizaciones/brl` — Real brasileño
- `GET /v1/cotizaciones/clp` — Peso chileno
- `GET /v1/cotizaciones/uyu` — Peso uruguayo

### 2. Cotizaciones Históricas
- `GET /v1/cotizaciones/dolares` — Historial completo de dólares
- `GET /v1/cotizaciones/dolares/blue` — Dólar blue histórico
- `GET /v1/cotizaciones/dolares/oficial` — Dólar oficial histórico
- `GET /v1/cotizaciones/dolares/bolsa` — Dólar bolsa (MEP)
- `GET /v1/cotizaciones/dolares/contadoconliqui` — CCL
- `GET /v1/cotizaciones/dolares/cripto` — Dólar cripto
- `GET /v1/cotizaciones/dolares/mayorista` — Dólar mayorista
- `GET /v1/cotizaciones/dolares/solidario` — Dólar solidario
- `GET /v1/cotizaciones/dolares/tarjeta` — Dólar tarjeta
- `GET /v1/cotizaciones/{año}` — Cotizaciones generales de un año específico (disponibles: 2023–2026)

### 3. Finanzas
- `GET /v1/finanzas/inflacion` — Inflación mensual
- `GET /v1/finanzas/tasas/plazoFijo` — Tasa actual de plazo fijo
- `GET /v1/finanzas/tasas/plazosFijos` — Tasas por entidad bancaria
- `GET /v1/finanzas/tasas/depositos30Dias` — Tasas de depósitos a 30 días
- `GET /v1/finanzas/indices` — Índice UVA
- `GET /v1/finanzas/fci` — Fondos comunes de inversión
- `GET /v1/finanzas/rendimientos` — Rendimientos
- `GET /v1/finanzas/creditos` — Créditos hipotecarios UVA
- `GET /v1/finanzas/hipotecarios-uva` — TNA hipotecarios UVA
- `GET /v1/finanzas/criptopesos` — Cotización criptopesos
- `GET /v1/finanzas/cuentas-remuneradas-usd` — Cuentas remuneradas en USD

> ❌ No implementar endpoints de otras categorías (`feriados`, `diputados`, `senado`, `eventos`, `estado`, etc.).

---

## Plan de Implementación Requerido

### Fase 1 — Análisis y Relevamiento
- Leer los archivos `.json` y `.yaml` de referencia en `\finanzas personales\`
- Explorar el repositorio `flagdipa/esjs-argentina-datos` (acceso desde Antigravity):
  - Revisar `cotizaciones.cron.esjs` y `finanzas.cron.esjs` para entender la lógica de extracción
  - Revisar los archivos en `src/cotizaciones/extraccion/` y `src/finanzas/extraccion/` para conocer parámetros y estructuras de respuesta
  - Explorar `datos/v1/` para entender el modelo de datos real de cada endpoint
- Documentar el esquema de datos de cada endpoint que será consumido

### Fase 2 — Arquitectura del Plugin
- Seguir la **estructura estándar de plugins del sistema 3F**
- Seguir los **skills y convenciones de desarrollo del sistema 3F**
- Definir la estructura de carpetas y archivos del plugin
- Definir el servicio de API (cliente HTTP, manejo de errores, reintentos)
- Definir los componentes visuales necesarios (widgets por endpoint, tablas, sidebar)
- Definir el store/estado del plugin

### Fase 3 — Base de Datos
- Si el plugin requiere persistencia, **agregar las tablas necesarias** a la base de datos
- ⚠️ **Prohibido modificar tablas existentes**. Solo se crean tablas nuevas con prefijo `argdat_`
- Documentar el esquema completo de cada tabla nueva

Tablas sugeridas a evaluar:
```sql
argdat_config          -- Configuración del plugin (intervalo, APIs activas)
argdat_cache           -- Caché de respuestas por endpoint
argdat_sync_log        -- Registro de sincronizaciones (fecha, estado, endpoint)
```

### Fase 4 — Configuración del Plugin
El panel de configuración debe permitir:
- ✅ Configurar el **intervalo de actualización automática** (ej: 15 min, 30 min, 1h, 4h, 24h)
- ✅ **Listar todos los endpoints** disponibles dentro del alcance (cotizaciones actuales, históricas y finanzas)
- ✅ **Activar o desactivar** individualmente cada endpoint/fuente de datos a visualizar
- ✅ La configuración se persiste en base de datos y se carga al iniciar el sistema

### Fase 5 — Interfaz de Usuario
- **Sidebar:** Cuando el plugin esté activo, aparece en la sección *Módulos* con el nombre **"Argentina Datos"**
- **Widgets:** Un widget por cada API/endpoint activado, mostrando el dato más reciente con su fecha de actualización
- **Tablas:** Opción de vista en tabla para datos que lo justifiquen (ej: cotizaciones históricas, tasas por entidad, FCI)
- **Botón de actualización manual:** Botón visible en la cabecera del módulo que fuerza la actualización de todos los datos activos
- **Indicadores de estado:** Cada widget indica si los datos están frescos, desactualizados o en error
- El diseño visual debe ser coherente con el sistema de diseño del sistema 3F

### Fase 6 — Lógica de Actualización
- Actualización automática según el intervalo configurado (usando scheduler/cron interno del sistema 3F)
- Actualización manual mediante el botón de actualización
- Caché de respuestas para evitar llamadas redundantes a la API
- Manejo de estados: `loading`, `success`, `error`, `stale`
- Manejo de errores HTTP y timeouts con feedback visual al usuario

### Fase 7 — Testing y Documentación
- Casos de prueba para cada endpoint consumido
- Pruebas de la lógica de actualización automática y manual
- Documentación del plugin: instalación, configuración, uso
- Documentación de las tablas nuevas en la base de datos

---

## Entregables Esperados

1. **Plan detallado** con fases, tareas priorizadas y orden de implementación
2. **Estructura de archivos** del plugin según convenciones del sistema 3F
3. **Esquema de base de datos** (solo tablas nuevas con prefijo `argdat_`)
4. **Código fuente** completo y funcional del plugin
5. **Documentación** técnica y de usuario del plugin

---

## Restricciones

- ❌ No modificar tablas existentes de la base de datos
- ❌ No consumir endpoints fuera de los grupos: cotizaciones actuales, cotizaciones históricas y finanzas
- ✅ Respetar la arquitectura, estructura de plugins y convenciones del sistema 3F
- ✅ Respetar los skills de desarrollo del sistema 3F

---
---

# 🔌 PROMPT 2 — Plugin: Cuentas / Billetera (Tasas de Interés)

---

## Contexto del Sistema

Eres un desarrollador senior del sistema **3F**. Tu tarea es **planificar e implementar** un módulo plugin de tasas de interés para este sistema. Debes seguir estrictamente los **skills, convenciones y estructura de plugins** establecidos en el proyecto 3F.

---

## Objetivo

Crear un plugin llamado **"Cuentas / Billetera"** que muestre las **tasas de interés ofrecidas por distintas entidades financieras** (bancos, billeteras digitales, fintechs) dentro del sistema 3F.

---

## Recursos Disponibles

| Recurso | Ubicación / URL |
|---|---|
| Servidor API | `https://api.argentinadatos.com` |
| Documentación online | `https://argentinadatos.com/docs/` |
| Repositorio local de APIs | `\finanzas personales\argentinadatos\comparatasas.ar-main` |
| Ejemplo de datos JSON | `\finanzas personales\argentinadatos_api.json` |
| Ejemplo de datos YAML | `\finanzas personales\argentinadatos_api.yaml` |

> ⚠️ **Antes de comenzar**, leer y analizar los archivos `.json`, `.yaml` y especialmente el repositorio local `comparatasas.ar-main` para comprender la estructura completa de las APIs disponibles, los endpoints expuestos y el modelo de datos de cada entidad financiera.

---

## Alcance de APIs a Consumir

El alcance exacto de endpoints a consumir debe determinarse **después de analizar el repositorio `comparatasas.ar-main`**. Como referencia general, el plugin debe cubrir:

1. **Tasas de interés actuales** ofrecidas por distintas entidades (bancos, fintechs, billeteras virtuales)
2. **Comparativas entre entidades** si el repositorio lo provee
3. **Datos históricos de tasas** si están disponibles en el repositorio
4. **Tipos de productos financieros** que el repositorio distinga (caja de ahorro remunerada, plazo fijo, cuenta corriente, etc.)

> ⚠️ El desarrollador debe explorar completamente el repositorio `comparatasas.ar-main` (estructura de carpetas, archivos de extracción, datos de ejemplo, README si existe) antes de definir el mapa definitivo de endpoints a implementar. Este análisis previo es obligatorio.

---

## Plan de Implementación Requerido

### Fase 1 — Análisis y Relevamiento
- Leer los archivos `.json` y `.yaml` de referencia en `\finanzas personales\`
- Explorar **completamente** el repositorio `comparatasas.ar-main`:
  - Estructura de carpetas y archivos
  - Archivos de extracción para entender los endpoints consumidos
  - Archivos de datos/ejemplos para conocer el modelo de respuesta
  - README o documentación interna si existe
- Mapear todos los endpoints disponibles relacionados con tasas de interés por entidad
- Documentar el esquema de datos de cada endpoint: campos, tipos, ejemplo de respuesta
- Identificar qué entidades financieras están disponibles y qué productos cubren

### Fase 2 — Arquitectura del Plugin
- Seguir la **estructura estándar de plugins del sistema 3F**
- Seguir los **skills y convenciones de desarrollo del sistema 3F**
- Definir la estructura de carpetas y archivos del plugin
- Definir el servicio de API (cliente HTTP, manejo de errores, reintentos)
- Definir los componentes visuales necesarios (widgets por entidad o producto, tablas comparativas, sidebar)
- Definir el store/estado del plugin

### Fase 3 — Base de Datos
- Si el plugin requiere persistencia, **agregar las tablas necesarias** a la base de datos
- ⚠️ **Prohibido modificar tablas existentes**. Solo se crean tablas nuevas con prefijo `cuentaswallet_`
- Documentar el esquema completo de cada tabla nueva

Tablas sugeridas a evaluar:
```sql
cuentaswallet_config        -- Configuración del plugin (intervalo, fuentes activas)
cuentaswallet_cache         -- Caché de respuestas por endpoint/entidad
cuentaswallet_sync_log      -- Registro de sincronizaciones
cuentaswallet_tasas_hist    -- Historial de tasas (si se desea persistir evolución)
```

### Fase 4 — Configuración del Plugin
El panel de configuración debe permitir:
- ✅ Configurar el **intervalo de actualización automática** (ej: 15 min, 30 min, 1h, 4h, 24h)
- ✅ **Listar todas las fuentes de datos/entidades** disponibles según el repositorio
- ✅ **Activar o desactivar** individualmente cada entidad o tipo de producto financiero a visualizar
- ✅ La configuración se persiste en base de datos y se carga al iniciar el sistema

### Fase 5 — Interfaz de Usuario
- **Sidebar:** Cuando el plugin esté activo, aparece en la sección *Módulos* con el nombre **"Cuentas / Billetera"**
- **Widgets:** Un widget por cada entidad o grupo activado, mostrando la tasa actual con su fecha de actualización
- **Tablas:** Vista en tabla comparativa de tasas entre entidades (este formato es especialmente relevante para comparar ofertas de distintas entidades de un vistazo)
- **Botón de actualización manual:** Botón visible en la cabecera del módulo que fuerza la actualización de todos los datos activos
- **Indicadores de estado:** Cada widget indica si los datos están frescos, desactualizados o en error
- El diseño visual debe ser coherente con el sistema de diseño del sistema 3F

### Fase 6 — Lógica de Actualización
- Actualización automática según el intervalo configurado (usando scheduler/cron interno del sistema 3F)
- Actualización manual mediante el botón de actualización
- Caché de respuestas para evitar llamadas redundantes
- Manejo de estados: `loading`, `success`, `error`, `stale`
- Manejo de errores HTTP y timeouts con feedback visual al usuario

### Fase 7 — Testing y Documentación
- Casos de prueba para cada endpoint consumido
- Pruebas de comparativa de tasas entre entidades
- Pruebas de la lógica de actualización automática y manual
- Documentación del plugin: instalación, configuración, uso
- Documentación de las tablas nuevas en la base de datos

---

## Entregables Esperados

1. **Plan detallado** con fases, tareas priorizadas y orden de implementación
2. **Mapa de endpoints** relevados del repositorio `comparatasas.ar-main`
3. **Estructura de archivos** del plugin según convenciones del sistema 3F
4. **Esquema de base de datos** (solo tablas nuevas con prefijo `cuentaswallet_`)
5. **Código fuente** completo y funcional del plugin
6. **Documentación** técnica y de usuario del plugin

---

## Restricciones

- ❌ No modificar tablas existentes de la base de datos
- ❌ No consumir endpoints fuera del alcance del repositorio `comparatasas.ar-main`
- ✅ Respetar la arquitectura, estructura de plugins y convenciones del sistema 3F
- ✅ Respetar los skills de desarrollo del sistema 3F