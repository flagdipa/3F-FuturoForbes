# PROMPT: Plugin "Argentina Datos" para el Sistema 3F

---

## 📋 CONTEXTO DEL SISTEMA

Estás desarrollando un **plugin nuevo** para **3F (Futuro Forbes)**, un sistema de gestión financiera personal construido con **FastAPI + SQLModel + AsyncIO**.

El sistema ya cuenta con una arquitectura de plugins funcional definida en `C:\xampp\htdocs\3F\PROMPT_PLUGINS.md`. **Debes leer ese archivo antes de comenzar**, ya que contiene la especificación completa de:

- El modelo de datos `Plugin` (tabla `plugins` en BD)
- La clase `BasePlugin` abstracta que todo plugin debe heredar
- El `PluginManager` y cómo registrar/activar/desactivar plugins
- Los hooks disponibles en el sistema
- La estructura de directorios que debe tener cada plugin
- Los endpoints de la API de plugins ya existentes
- La interfaz frontend `plugins.html` ya existente

---

## 🎯 OBJETIVO

Implementar el plugin **"Argentina Datos"** que consuma las APIs públicas de [argentinadatos.com](https://argentinadatos.com) para mostrar información financiera argentina actualizada dentro del sistema 3F.

El plugin debe:
1. Aparecer correctamente en el sistema de plugins del sistema 3F (listado, activación, desactivación)
2. Tener su **panel de configuración completo y funcional** accesible desde la interfaz de plugins
3. Mostrar sus widgets/datos en el **sidebar** de la aplicación en la sección *Módulos*, con el nombre **"Argentina Datos"**
4. Actualizarse automáticamente según el intervalo configurado y permitir actualización manual

---

## 📁 RECURSOS DISPONIBLES

| Recurso | Ruta / URL |
|---|---|
| Arquitectura base de plugins del sistema | `C:\xampp\htdocs\3F\PROMPT_PLUGINS.md` |
| Repositorio GitHub del proveedor de datos | `https://github.com/flagdipa/esjs-argentina-datos.git` |
| Ruta local del repositorio de datos | `C:\xampp\htdocs\finanzas personales\argentinadatos` |
| Servidor API público | `https://api.argentinadatos.com` |
| Documentación oficial de la API | `https://argentinadatos.com/docs/` |
| Archivo de referencia JSON | `C:\xampp\htdocs\finanzas personales\argentinadatos_api.json` |
| Archivo de referencia YAML | `C:\xampp\htdocs\finanzas personales\argentinadatos_api.yaml` |

> ⚠️ El repositorio GitHub `flagdipa/esjs-argentina-datos` es accesible desde **Antigravity**. Explorarlo junto con los archivos JSON/YAML de referencia para entender la estructura real de cada endpoint antes de comenzar a codificar.

---

## 🏗️ ARQUITECTURA BASE DEL SISTEMA 3F (resumen)

El sistema 3F ya tiene definido en `PROMPT_PLUGINS.md` lo siguiente. El plugin **debe respetar todo esto**:

### Modelo de datos `Plugin` (ya existe, no modificar):
```python
class Plugin(SQLModel, table=True):
    __tablename__ = "plugins"
    id_plugin: Optional[int]
    nombre_tecnico: str          # Identificador único: "argentina_datos"
    nombre_display: str          # "Argentina Datos"
    descripcion: Optional[str]
    version: str                 # "1.0.0"
    autor: str
    instalado: bool
    activo: bool
    configuracion: Dict[str, Any]  # JSON con toda la config del plugin
    hooks_suscritos: str           # Comma-separated
    creado_el: datetime
    actualizado_el: datetime
```

### Clase base que el plugin debe heredar:
```python
class BasePlugin(ABC):
    nombre_tecnico: str
    nombre_display: str
    version: str
    autor: str
    descripcion: str
    hooks: List[str]

    async def initialize(self): ...   # OBLIGATORIO implementar
    async def shutdown(self): ...     # OBLIGATORIO implementar
    async def on_hook(self, hook_name, **kwargs): ...
```

### Estructura de directorios del plugin:
```
backend/plugins/argentina_datos/
├── __init__.py
├── plugin.py          ← Clase principal ArgentinaDatosPlugin(BasePlugin)
├── services.py        ← Lógica de consumo de APIs
├── requirements.txt   ← Dependencias extras (httpx, etc.)
└── README.md
```

### Hooks del sistema disponibles (usar los que correspondan):
- `daily_summary` — para disparar actualización diaria automática
- `data_export` — si se desea exportar datos
- `report_generate` — si se desea generar reportes

---

## ⚙️ CONFIGURACIÓN DEL PLUGIN — ESPECIFICACIÓN DETALLADA

Este es el punto crítico que falló en la implementación anterior. La configuración debe:

1. **Almacenarse** en el campo `configuracion` (JSON) del modelo `Plugin` existente
2. **Editarse** desde la interfaz web de plugins ya existente (`plugins.html`) mediante el modal de configuración dinámico que ya tiene el sistema
3. **Cargarse** correctamente al inicializar el plugin (`initialize()`)
4. **Validarse** con schema JSON antes de guardar

### Schema JSON de configuración del plugin:

```json
{
  "intervalo_actualizacion_minutos": 60,

  "apis_disponibles": {
    "cotizaciones_actuales": {
      "label": "Cotizaciones actuales (todas las divisas)",
      "endpoint": "/v1/cotizaciones",
      "activa": true
    },
    "dolar_blue": {
      "label": "Dólar Blue (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/blue",
      "activa": true
    },
    "dolar_oficial": {
      "label": "Dólar Oficial (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/oficial",
      "activa": false
    },
    "dolar_bolsa": {
      "label": "Dólar Bolsa / MEP (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/bolsa",
      "activa": false
    },
    "dolar_ccl": {
      "label": "Dólar CCL (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/contadoconliqui",
      "activa": false
    },
    "dolar_cripto": {
      "label": "Dólar Cripto (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/cripto",
      "activa": false
    },
    "dolar_mayorista": {
      "label": "Dólar Mayorista (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/mayorista",
      "activa": false
    },
    "dolar_tarjeta": {
      "label": "Dólar Tarjeta (histórico)",
      "endpoint": "/v1/cotizaciones/dolares/tarjeta",
      "activa": false
    },
    "euro": {
      "label": "Euro",
      "endpoint": "/v1/cotizaciones/eur",
      "activa": false
    },
    "real": {
      "label": "Real Brasileño",
      "endpoint": "/v1/cotizaciones/brl",
      "activa": false
    },
    "inflacion": {
      "label": "Inflación mensual",
      "endpoint": "/v1/finanzas/inflacion",
      "activa": true
    },
    "plazo_fijo": {
      "label": "Tasas de Plazo Fijo",
      "endpoint": "/v1/finanzas/tasas/plazoFijo",
      "activa": false
    },
    "plazos_fijos_entidades": {
      "label": "Tasas por entidad bancaria",
      "endpoint": "/v1/finanzas/tasas/plazosFijos",
      "activa": false
    },
    "depositos_30_dias": {
      "label": "Depósitos a 30 días",
      "endpoint": "/v1/finanzas/tasas/depositos30Dias",
      "activa": false
    },
    "indice_uva": {
      "label": "Índice UVA",
      "endpoint": "/v1/finanzas/indices",
      "activa": false
    },
    "fci": {
      "label": "Fondos Comunes de Inversión",
      "endpoint": "/v1/finanzas/fci",
      "activa": false
    },
    "riesgo_pais": {
      "label": "Riesgo País",
      "endpoint": "/v1/finanzas/rendimientos",
      "activa": false
    },
    "criptopesos": {
      "label": "Criptopesos",
      "endpoint": "/v1/finanzas/criptopesos",
      "activa": false
    },
    "cuentas_remuneradas_usd": {
      "label": "Cuentas Remuneradas USD",
      "endpoint": "/v1/finanzas/cuentas-remuneradas-usd",
      "activa": false
    },
    "hipotecarios_uva": {
      "label": "Hipotecarios UVA (TNA)",
      "endpoint": "/v1/finanzas/hipotecarios-uva",
      "activa": false
    },
    "creditos_hipotecarios": {
      "label": "Créditos Hipotecarios UVA",
      "endpoint": "/v1/finanzas/creditos",
      "activa": false
    }
  }
}
```

### Cómo debe funcionar la configuración:

- Al abrir el modal de configuración del plugin desde `plugins.html`, se debe mostrar:
  1. Un campo numérico para el **intervalo de actualización** (en minutos)
  2. Una **lista de checkboxes**, uno por cada API en `apis_disponibles`, mostrando el `label` y el estado `activa`
- Al guardar, el JSON completo se actualiza en el campo `configuracion` de la tabla `plugins`
- Al activar el plugin, `initialize()` debe leer `self.config["apis_disponibles"]` y registrar únicamente las APIs con `activa: true`
- La actualización automática usa el `intervalo_actualizacion_minutos` para programar el scheduler

---

## 📡 ESTRUCTURA DEL REPOSITORIO DE DATOS (referencia)

El repositorio `flagdipa/esjs-argentina-datos` (path local: `C:\xampp\htdocs\finanzas personales\argentinadatos`) está organizado así:

```
esjs-argentina-datos/
├── api/
│   └── api.esjs        ← Servidor Hono: registra rutas dinámicas desde /datos
├── src/
│   ├── cotizaciones/
│   │   ├── cotizaciones.cron.esjs    ← extrae cotizaciones y dólares
│   │   └── extraccion/
│   │       ├── extraerCotizaciones.esjs
│   │       └── extraerDolares.esjs
│   └── finanzas/
│       ├── finanzas.cron.esjs        ← orquesta todos los extractores de finanzas
│       └── extraccion/               ← inflación, plazo fijo, UVA, FCI, etc.
└── datos/
    └── v1/
        ├── cotizaciones/
        │   ├── index.json            ← cotizaciones actuales
        │   ├── dolares/              ← historial 2011–2026: blue, oficial, bolsa,
        │   │                            ccl, cripto, mayorista, solidario, tarjeta
        │   └── eur/, brl/, clp/, uyu/
        └── finanzas/
            ├── inflacion/
            ├── tasas/
            │   ├── plazoFijo/
            │   ├── plazosFijos/
            │   └── depositos30Dias/
            ├── indices/              ← UVA
            ├── fci/
            ├── rendimientos/
            ├── creditos/
            ├── hipotecarios-uva/
            ├── criptopesos/
            └── cuentas-remuneradas-usd/
```

> 💡 Cada carpeta con `index.json` se convierte en un endpoint accesible en `https://api.argentinadatos.com/v1/...`

---

## 🗄️ BASE DE DATOS

Si el plugin necesita persistencia propia (caché, historial, log de sincronizaciones):

- ✅ Crear **solo tablas nuevas** con prefijo `argdat_`
- ❌ **Prohibido modificar tablas existentes** (incluyendo la tabla `plugins`)

Tablas sugeridas a evaluar:
```sql
-- Caché de respuestas por endpoint
CREATE TABLE argdat_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    datos JSON NOT NULL,
    actualizado_el DATETIME NOT NULL,
    UNIQUE KEY uk_endpoint (endpoint)
);

-- Log de sincronizaciones
CREATE TABLE argdat_sync_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(200),
    estado ENUM('ok', 'error') NOT NULL,
    mensaje TEXT,
    ejecutado_el DATETIME NOT NULL
);
```

---

## 🖥️ INTERFAZ DE USUARIO

### En el sidebar (sección Módulos):
- Cuando el plugin esté **activo**, aparece en el sidebar con el nombre **"Argentina Datos"**
- Al hacer clic muestra los widgets/datos de las APIs que tienen `activa: true` en la configuración

### Widgets:
- Un widget por cada API activa
- Cada widget muestra: nombre del dato, valor actual, fecha/hora de última actualización
- Estado visual: 🟢 fresco / 🟡 desactualizado / 🔴 error

### Tablas:
- Para datos con múltiples filas (ej: tasas por entidad, historial de cotizaciones, FCI) ofrecer opción de vista en tabla además del widget

### Botón de actualización manual:
- Botón visible en la cabecera del módulo "Argentina Datos" en el sidebar
- Al presionarlo, fuerza la actualización inmediata de todas las APIs activas
- Muestra spinner durante la actualización y feedback de éxito/error al terminar

---

## 🔄 LÓGICA DE ACTUALIZACIÓN

```python
class ArgentinaDatosPlugin(BasePlugin):
    nombre_tecnico = "argentina_datos"
    nombre_display = "Argentina Datos"
    hooks = ["daily_summary"]

    async def initialize(self):
        # 1. Leer self.config["apis_disponibles"]
        # 2. Filtrar las que tienen activa=True
        # 3. Registrar el scheduler con self.config["intervalo_actualizacion_minutos"]
        # 4. Ejecutar primera carga de datos
        ...

    async def on_daily_summary(self, **kwargs):
        # Actualizar todas las APIs activas
        await self._actualizar_todas()

    async def _actualizar_todas(self):
        apis_activas = [
            (key, cfg) for key, cfg in self.config["apis_disponibles"].items()
            if cfg["activa"]
        ]
        for key, cfg in apis_activas:
            try:
                datos = await self._fetch(cfg["endpoint"])
                await self._guardar_cache(cfg["endpoint"], datos)
            except Exception as e:
                self.logger.error(f"Error actualizando {key}: {e}")

    async def _fetch(self, endpoint: str):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"https://api.argentinadatos.com{endpoint}")
            response.raise_for_status()
            return response.json()

    async def shutdown(self):
        # Cancelar scheduler, cerrar conexiones
        ...
```

---

## 🔌 ENDPOINT DE ACTUALIZACIÓN MANUAL

Agregar al router de plugins o crear endpoint propio:

```python
@router.post("/argentina_datos/actualizar")
async def actualizar_argentina_datos():
    """Fuerza actualización manual de todas las APIs activas del plugin"""
    plugin = plugin_manager.get_plugin_instance("argentina_datos")
    if not plugin:
        raise HTTPException(404, "Plugin no activo")
    await plugin._actualizar_todas()
    return {"status": "ok", "mensaje": "Datos actualizados"}

@router.get("/argentina_datos/datos")
async def obtener_datos_argentina():
    """Retorna los datos cacheados de todas las APIs activas"""
    plugin = plugin_manager.get_plugin_instance("argentina_datos")
    if not plugin:
        raise HTTPException(404, "Plugin no activo")
    return await plugin.obtener_datos_cacheados()
```

---

## 📋 PLAN DE IMPLEMENTACIÓN

### Fase 1 — Lectura y análisis (OBLIGATORIO antes de codificar)
- Leer completamente `C:\xampp\htdocs\3F\PROMPT_PLUGINS.md`
- Revisar el plugin de ejemplo `dolar_hoy` en `backend/plugins/dolar_hoy/` (si existe) como referencia
- Explorar el repositorio `flagdipa/esjs-argentina-datos` y los archivos JSON/YAML de referencia
- Mapear el modelo de datos de cada endpoint a consumir

### Fase 2 — Creación del plugin
- Crear `backend/plugins/argentina_datos/__init__.py`
- Crear `backend/plugins/argentina_datos/plugin.py` — clase `ArgentinaDatosPlugin(BasePlugin)`
- Crear `backend/plugins/argentina_datos/services.py` — cliente HTTP y lógica de caché
- Crear `backend/plugins/argentina_datos/requirements.txt` — dependencias (httpx, etc.)
- Crear `backend/plugins/argentina_datos/README.md`

### Fase 3 — Base de datos
- Crear migración/script SQL para las tablas `argdat_cache` y `argdat_sync_log`
- Integrar el guardado/lectura de caché en `services.py`

### Fase 4 — Configuración (punto crítico)
- Asegurar que `initialize()` lee y valida correctamente `self.config`
- Implementar el schema JSON de configuración completo (todas las APIs listadas)
- Verificar que el modal de configuración en `plugins.html` muestra y guarda correctamente:
  - El campo de intervalo de actualización
  - El listado de checkboxes de APIs (una por cada entrada de `apis_disponibles`)
- Implementar validación del schema antes de persistir

### Fase 5 — API endpoints
- Endpoint `POST /plugins/argentina_datos/actualizar` — actualización manual
- Endpoint `GET /plugins/argentina_datos/datos` — datos cacheados para el frontend
- Registrar el plugin en el `PluginManager` del sistema

### Fase 6 — Frontend (sidebar + widgets)
- Agregar entrada de "Argentina Datos" al sidebar en la sección *Módulos* (visible solo cuando el plugin está activo)
- Implementar widgets para cada API activa
- Implementar vista tabla donde corresponda
- Implementar botón de actualización manual con spinner y feedback
- Implementar indicadores de estado (fresco/desactualizado/error) por widget

### Fase 7 — Testing y documentación
- Tests unitarios: `initialize()`, `_fetch()`, `_actualizar_todas()`, schema de config
- Test de integración: hook `daily_summary` dispara actualización
- Test de aislamiento: error en una API no detiene las demás
- Documentar en `README.md` del plugin: instalación, configuración, uso

---

## ✅ CRITERIOS DE ACEPTACIÓN

- [ ] El plugin aparece correctamente en el listado de plugins (`plugins.html`)
- [ ] Se puede instalar, activar y desactivar desde la interfaz
- [ ] El modal de configuración muestra el intervalo de actualización y la lista completa de APIs con checkboxes para activar/desactivar cada una individualmente
- [ ] La configuración se guarda y se carga correctamente (sin perder datos entre reinicios)
- [ ] Al activar, solo se cargan las APIs marcadas como activas
- [ ] "Argentina Datos" aparece en el sidebar cuando el plugin está activo
- [ ] Los widgets muestran datos actualizados de cada API activa
- [ ] El botón de actualización manual funciona y da feedback visual
- [ ] La actualización automática respeta el intervalo configurado
- [ ] Un error en una API no impide la actualización de las demás
- [ ] No se modifican tablas existentes de la base de datos
- [ ] No se consumen endpoints fuera del alcance definido

---

## 🚫 RESTRICCIONES

- ❌ No modificar tablas existentes de la base de datos (incluyendo `plugins`)
- ❌ No consumir endpoints fuera de: cotizaciones actuales, cotizaciones históricas de dólares y finanzas
- ❌ No consumir endpoints de categorías ajenas (`feriados`, `diputados`, `senado`, `eventos`, `estado`)
- ✅ Seguir exactamente la arquitectura de plugins definida en `C:\xampp\htdocs\3F\PROMPT_PLUGINS.md`
- ✅ Heredar de `BasePlugin` e implementar `initialize()` y `shutdown()`
- ✅ Usar AsyncIO / httpx para llamadas HTTP (no requests sincrónico)
- ✅ Aislar errores: un fallo no debe detener el sistema ni otros plugins

---

**Sistema:** 3F (Futuro Forbes)  
**Stack:** FastAPI + SQLModel + AsyncIO  
**Plugin:** argentina_datos v1.0.0  
**Repositorio de datos:** https://github.com/flagdipa/esjs-argentina-datos.git