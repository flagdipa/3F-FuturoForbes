# Spec: Temas y Customización

## Goal
Documentar la experiencia de usuario personalizada mediante selección de pieles Visuales (Themes) y configuraciones de Grid dinámico, asegurando persistencia de estado por usuario para entornos colaborativos o multi-usuario futuros.

## Capabilities
1. **Gestión de Temas (Apperance) y Modo Sidebar:** Soportar UI mode Dark/Light por defecto y CSS puro ("Cyberpunk", "Neon") guardadas en la string `theme`. El navbed sidebar debe poseer persistencia y un comportamiento de colapso a tamaño "ícono-only" en lugar de ocultarse totalmente de la pantalla para mantener contexto.
2. **Layouts de GridStack.js:** Configuración guardada explícitamente sobre el x/y/w/h de los widgets del Dashboard haciendolo enteramente reponsivo y personalizable en capa frontend. (`PUT /config/layout`).
3. **Selector Activo de Widgets:** Existirá una ventana, modal o panel lateral que listará con minúsculos checkboxes de activación/desactivación rápida qué widgets el usuario quiere cargar en el centro de control.

## Data Models
En la tabla `User` interactúan las columnas `theme` y variables de sesión. Configuraciones extensas podrían acoplarse también como JSON extra si aplica.

## API Endpoints (`/api/auth`)
- `GET /profile/dashboard-layout` - Recupera la configuración de widgets guardada.
- `POST /profile/dashboard-layout` - Guarda la nueva disposición o set de widgets activos.
- `POST /profile` - Actualiza preferencias generales como `theme_id` y `language`.
