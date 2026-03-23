# Especificación Delta: Transacciones Recurrentes (UX / MMEX)

## Capabilities

Actualización profunda sobre la experiencia de manejo temporal. Inspirado completamente en la fluidez de *MoneyManagerEX*:

1. **Vista de Calendario Interactivo:**
   - La lista tradicional de recurrencias se reemplaza (o suma como vista principal) por una "Vista de Calendario" (ej. integración con FullCalendar.js o librería similar en el DOM).
   - En este calendario, el usuario visualizará los "hits" o puntos de cobro/pago proyectados de cada transacción programada.

2. **Acciones Rápidas (CRUD on Calendar):**
   - El propio overlay del calendario debe presentar botones globales claros para: **Crear**, **Borrar** o **Modificar**.
   - Evento *On-Click*: Al hacer clic sobre cualquier evento recurrente que ya esté renderizado en un día específico del calendario, se disparará el modal o formulario correspondiente para permitir la edición o cancelación rápida de esa regla.
