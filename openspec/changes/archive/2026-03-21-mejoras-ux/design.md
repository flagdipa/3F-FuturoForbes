## Context
Plan de transformación visual y de usabilidad del Frontend de 3F para enriquecer la experiencia de usuario general incorporando "quality of life features".

## Goals
- **Sidebar**: Mantener contexto visual (íconos) al minimizar.
- **Entidades Financieras**: CRUD gráfico 1:1 con la experiencia de gestión de Categorías + Íconos. Las Cuentas se deben atar directamente a estas.
- **Lista de Cuentas**: Grid tabular estilo DataTables en vez de simples cards.
- **Calendario Recurrente**: Dejar las listas planas y pasar a un FullCalendar intuitivo con soporte de edición on-click.
- **Widgets Checkbox**: Un modal o panel de "Añadir Widget" donde simples checkboxes inyectan los módulos en el GridStack de forma responsiva.

## Migration Plan
1. Alterar especificación `temas-customizacion` sumando el comportamiento Sidebar y el selector Checkbox para widgets.
2. Alterar especificación `core-financiero` sumando el CRUD de Entidades y la visual de Cuentas tabular.
3. Alterar especificación `transacciones-recurrentes` sumando el UI de Calendario interactivo (MMEX based).
4. Generar las tareas correspondientes.
