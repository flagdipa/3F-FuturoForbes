# Proposal: Reorganize Sidebar with Drag-and-Drop

## What

Este cambio propone una reorganización funcional y visual del sidebar del sistema 3F para hacerlo más dinámico, modular y personalizable por el usuario. Los cambios principales son:

1. **Orden y Categorización Base**: Se establecerá una estructura clara comenzando por Dashboard, Transacciones programadas, Transacciones en $ y Transacciones en u$s. Luego vendrán secciones para Presupuestos, Metas, Comprobantes, Configuración, etc.
2. **Cuentas Dinámicas por Tipo**: Las cuentas ya no se agruparán bajo un solo ítem "Cuentas", sino que se desglosarán en categorías específicas en el sidebar: Cuentas Favoritas, Cuentas bancarias, Cuentas Tarjeta de crédito, Cuentas billeteras, Cuentas en efectivo, Cuentas a plazo, etc. A medida que se creen nuevos tipos de cuentas en el sistema, estas aparecerán como nuevos grupos/ítems en el sidebar.
3. **Soporte para Plugins/Módulos**: Se sumará un agrupador o sección "Módulos" que renderizará dinámicamente los menús de aquellos plugins que estén activados en el sistema (ej. leyendo el endpoint de plugins activos).
4. **Drag and Drop (Reordenamiento)**: Se integrará la funcionalidad de arrastrar y soltar (SortableJS) en el frontend. El usuario podrá reordenar las secciones/ítems del sidebar según sus preferencias, y este orden quedará guardado persistentemente en la base de datos vinculado a su perfil.

## Why

El sidebar actual es mayormente estático. A medida que el ecosistema de 3F evoluciona, el usuario requiere:
* **Mejor acceso a sus activos financieros**: Separar cuentas por "tipo" en el menú principal permite ir directamente al subconjunto de interés sin varios clics.
* **Escalabilidad Modular**: Al instalar y activar nuevos plugins (módulos), la UI debe reaccionar sola para exponer esas nuevas herramientas, haciendo al framework 3F verdaderamente extensible.
* **Personalización del Espacio de Trabajo**: Cada usuario gestiona sus finanzas distinto; algunos usan más Presupuestos, otros más Inversiones. El Drag & Drop otorga libertad para priorizar lo relevante, mejorando enormemente la Experiencia de Usuario (UX).

## Impact

* **Frontend**:
  * Modificación estructural en `frontend/templates/modules/sidebar.html` para soportar renderizado dinámico por bloques iterables en Alpine.
  * Cambios profundos en `sidebar-manager.js` (y `Alpine.store('sidebar')`) para procesar la agrupación de cuentas por tipo, instanciar SortableJS gestionando eventos de arrastre, y aplicar el orden preferido.
* **Backend**:
  * Creación/Uso de una estructura para guardar las preferencias de usuario (`SystemConfig` con clave por usuario, `CustomField` asocida al User, o extender el modelo `User`). Se creará o ajustará un endpoint para guardar y recuperar el JSON del "orden del sidebar".
  * El frontend se apoyará fuertemente en respuestas existentes como `/api/v1/plugins/activos` y `/api/v1/accounts` (para agrupar en lado cliente por enum `type`).
