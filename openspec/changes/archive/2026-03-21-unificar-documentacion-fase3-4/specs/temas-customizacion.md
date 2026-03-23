# Spec: Temas y Customización

## Goal
Documentar la experiencia de usuario personalizada mediante selección de pieles Visuales (Themes) y configuraciones de Grid dinámico, asegurando persistencia de estado por usuario para entornos colaborativos o multi-usuario futuros.

## Capabilities
1. **Gestión de Temas (Apperance):** Soportar UI mode Dark/Light por defecto, más inyecciones de CSS puro ("Cyberpunk", "Neon") guardadas en la string `theme` del usuario. Redibujado en capa Frontend (Alpine).
2. **Layouts de GridStack.js:** Configuración guardada explícitamente sobre el x/y/w/h de los widgets del Dashboard. `PUT /config/layout`.

## Data Models
En la tabla `User` interactúan las columnas `theme` y variables de sesión. Configuraciones extensas podrían acoplarse también como JSON extra si aplica.

## API Endpoints (`/api/v1/config`)
- `GET /themes` - Listado estático (o dinámico) de hojas de estilo posibles.
- `PUT /theme` - Setea estilo predominante.
- `GET /layout`, `PUT /layout` - Lectura/Escritura de la grilla personalizada.
