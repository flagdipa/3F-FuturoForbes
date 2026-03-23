# Design: Reorganize Sidebar with Drag-and-Drop

## Context

Actualmente, el sidebar del sistema (definido en `frontend/templates/modules/sidebar.html`) renderiza los menúes de navegación en un orden estático. Aunque integra reactividad mediante AlpineJS (`Alpine.store('sidebar')`) para inyectar la lista de cuentas separadas por moneda (Pesos/Dólares) interactuando con el backend, no agrupa las cuentas por su naturaleza real (Bancos, Billeteras, Tarjetas de Crédito, etc.) ni mapea plugins de forma puramente dinámica bajo una sección "Módulos". Además, el usuario no puede priorizar (reordenar) sus componentes principales.

El objetivo es migrar este menú a un modelo de configuración basado en datos, donde el estado principal resida en un array o JSON dictando el orden y contenido, permitiendo la funcionalidad de Drag & Drop y el agrupamiento de sub-ítems según las reglas del negocio de los modelos actualizados.

## Goals

* Transformar la renderización del sidebar en `sidebar.html` iterando una lista estructurada, permitiendo que `SortableJS` controle el DOM y persistiendo los cambios de orden.
* Agrupar las cuentas que vienen de `/api/v1/accounts/` en categorías específicas: "Cuentas Favoritas", "Cuentas bancarias", "Cuentas Tarjeta de crédito", "Cuentas billeteras", "Cuentas en efectivo", "Cuentas a plazo", guiado por los metadatos o tipos de las mismas (ej. `AccountType`).
* Reflejar automáticamente la aparición de herramientas nuevas cuando se activan (plugins) iterando los resultados de `/api/v1/plugins/activos` bajo un menú padre "Módulos".
* Conservar el orden establecido de forma permanente, independientemente de la sesión.

## Architecture / Design

1. **Estado en AlpineJS (`sidebar-manager.js`)**: 
   * Se introducirá un nuevo estado reactivo, e.g. `menuStructure`, que contendrá el ordenamiento de los grandes bloques. 
   * Se modificara el parseo de cuentas devueltas por la API para dividirlas en arreglos o sub-listas: `banks`, `wallets`, `credit_cards`, `cash`, etc. (Este mapeo se hará inicialmente cruzando el campo `type` de `AccountType` o buscando palabras clave/subtipos si el campo `institution_id` da pistas de que es un banco vs billetera).
   
2. **HTML / Jinja Templates**:
   * El `<ul>` principal del sidebar iterará sobre el orden lógico obtenido.
   * Los sub-bloques de Módulos (plugins) se construirán usando `<template x-for="...">` con la info cargada de la API correspondiente.
   
3. **Drag and Drop (`SortableJS`)**:
   * SortableJS ya está importado en `base.html`. Al inicializarse el store de Alpine, se atará `new Sortable(document.getElementById('sidebar-menu-list'), { ... })`.
   * En el hook `onEnd` de Sortable, se calculará el nuevo array con las claves (ej. `['dashboard', 'tx_scheduled', 'tx_ars', 'tx_usd', 'acc_favs', 'acc_banks', ...]`) y se despachará asíncronamente al backend para guardar.
   
4. **Persistencia Backend**:
   * Para evitar modificar los Core Models, se utilizará el sistema existente de preferencias, posiblemente `CustomField` con `entity_type: 'USER_PREFERENCE'` o bien la tabla `SystemConfig` usando métricas nombradas dinámicamente (`sidebar_order_user_{ID}`).
   * Se desarrollará o modificará un endpoint (e.g. `PUT /api/v1/config/sidebar-preferences`) para hacer persistente el perfil u orden.

## Database Changes

En principio, **no se requieren cambios al esquema (migrations)**, logrando alinear el cambio a las normas arquitectónicas "no disruptivas" de 3F v2:
* Se utilizará el modelo de sistema clave-valor provisto: `SystemConfig` (asociando la clave a "sidebar_order_user_`<id>`") o creando un modelo de Pydantic para guardarlo como metadata genérica.
  
## APIs

* No son necesarias APIs nuevas para plugins (se usa `/api/v1/plugins/activos` o raíz).
* No hay cambios grandes en `/api/v1/accounts/`.
* Se necesita un endpoint ligero para GET/PUT del layout: 
  * `GET /api/v1/users/me/ui-preferences`
  * `PUT /api/v1/users/me/ui-preferences` 
  *(O reusar endpoints de settings generales del sistema para el perfil del solicitante).*

## Risks / Trade-offs

* **Rendimiento Visual (FOUC)**: Como Alpine y Sortable renderizarán en el frontend luego de un AJAX (*fetch UI preferences*), tal vez haya un pequeño destello visual en lo que el contenido toma su orden. Un mitigante es inyectar el orden inicial en Jinja si está disponible síncronamente en el contexto del request.
* **Clasificación Automática de Cuentas**: Si el modelo `Account` no diferencia explícitamente entre Billetera y Banco (usando en el backend a lo sumo `ASSET` o `LIABILITY`), el código JS del frontend deberá inferirlo buscando palabras (e.g. "MercadoPago", "Uala" -> Billeteras; "Galicia", "Santander" -> Bancos). Esto es frágil si el usuario usa nombres particulares no estandarizados, pero es el trade-off con mayor inmediatez si no se quiere obligar a migraciones engorrosas de bases de datos de inmediato.
