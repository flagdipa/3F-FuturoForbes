# Especificación Delta: Temas y Customización (UX)

## Capabilities

Esta especificación modifica el comportamiento general de la UI del Frontend:

1. **Estado del Sidebar (Minimizado Constante):**
   - Cuando el usuario acciona el botón de ocultar la barra lateral (Sidebar Toggle), en lugar de ocultarse la ventana fuera del viewport (off-canvas total), esta debe colapsar a un ancho reducido (aprox `50px`) dejando únicamente visibles los íconos de cada menú.
   - Mejora fuertemente la retención de contexto de navegación en pantallas de escritorio.

2. **Personalización del Centro de Control (Dashboard Widgets):**
   - El layout basado en GridStack debe de volverse completamente responsivo a la grilla que el usuario decida (drag and drop y resize).
   - **Gestor de Widgets**: Se incorpora un panel de configuración o modal donde aparecerán todos los widgets disponibles del sistema acompañados de un checkbox o "switch" pequeño. Al tildar este checkbox, el widget se agregará automáticamente al canvas del Dashboard; al destildarlo, se quitará dinámicamente y la grilla se reacomodará.
