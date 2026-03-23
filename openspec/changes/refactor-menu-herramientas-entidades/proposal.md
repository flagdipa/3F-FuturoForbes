# Proposal: Refactor Menú Herramientas y Entidades

## Why

El menú superior actual tiene el dropdown "Herramientas" que ocupa espacio innecesario con texto. Se desea simplificar la interfaz mostrando solo el ícono de herramientas (screwdriver-wrench) sin texto, liberando espacio en la barra de navegación.

Además, la opción "Tipos de Financiera" dentro del menú Herramientas debe eliminarse de ese menú y convertirse en un ícono accesible directamente desde la ventana de "Gestión de Financieras" (actualmente accesible desde el menú).

Finalmente, se requiere actualizar la terminología en el diccionario español, cambiando todas las referencias de "Financieras" a "Entidades" para mantener consistencia semántica.

## What Changes

- **Menú Superior**: Eliminar el texto "Herramientas" del menú dropdown, dejando solo el ícono `fa-screwdriver-wrench`
- **Menú Herramientas**: Remover la opción "Tipos de Financiera" del dropdown
- **Ventana Entidades**: Agregar un ícono/botón en la interfaz de gestión de entidades para acceder a "Tipos de Entidad"
- **Diccionario Español**: Actualizar todas las claves que contengan "financiera(s)" para usar "entidad(es)" en su lugar

## Capabilities

### New Capabilities
- *(Ninguna capacidad nueva)*

### Modified Capabilities
- `menu-herramientas`: El menú dropdown pasa de mostrar texto+ícono a solo ícono
- `menu-entidades`: Agregar acceso a tipos de entidad desde la ventana de gestión
- `diccionario-es`: Actualizar terminología financieras → entidades

## Impact

- **Archivos afectados**:
  - `frontend/templates/base.html` - Modificar estructura del menú Herramientas
  - `frontend/static/js/lang-es.json` - Actualizar claves de traducción
  - `frontend/templates/entidades/index.html` - Agregar ícono de tipos de entidad (si existe)
  - Posiblemente `frontend/static/js/lang-en.json` - Mantener consistencia en inglés

- **UI/UX**: Interfaz más limpia con menos texto en la barra superior
- **Compatibilidad**: Los usuarios accederán a "Tipos" desde la ventana de entidades en lugar del menú superior
- **Internacionalización**: Cambio en las claves de idioma español

