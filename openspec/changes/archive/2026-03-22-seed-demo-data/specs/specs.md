# Specs: Seed Demo Data

## BDD Requirements

### Requirement: Script principal idempotente
- **GIVEN** una base de datos local del sistema 3F (SQLite o PostgreSQL)
- **WHEN** se ejecuta `python -m backend.scripts.seed_demo`
- **THEN** se crea un usuario `demo@3f.local` con password `demo123` si no existe
- **AND** se crean cuentas, categorías, beneficiarios, tags y transacciones vinculados a ese usuario
- **AND** los balances de cuenta reflejan correctamente las transacciones insertadas

### Requirement: No duplica datos
- **GIVEN** que el seed ya fue ejecutado una vez
- **WHEN** se corre el script nuevamente sin `--force`
- **THEN** el script detecta el usuario demo existente y termina con un mensaje
- **AND** NO se duplica ningún registro

### Requirement: Reset con --force
- **GIVEN** que el seed ya fue ejecutado
- **WHEN** se corre `python -m backend.scripts.seed_demo --force`
- **THEN** se eliminan todos los datos del usuario demo
- **AND** se vuelve a crear todo desde cero

### Requirement: Script de limpieza
- **GIVEN** datos de demo en la base de datos
- **WHEN** se ejecuta `python -m backend.scripts.clear_demo`
- **THEN** se eliminan SOLO los registros del usuario `demo@3f.local`
- **AND** los datos de otros usuarios NO son afectados

### Requirement: Datos cuantitativamente suficientes para pruebas UI
- **GIVEN** el script ejecutado exitosamente
- **WHEN** se abre el sistema en el browser como el usuario demo
- **THEN** el Libro de Transacciones muestra al menos 200 registros
- **AND** el Dashboard muestra balance consolidado real > 0
- **AND** los filtros por cuenta, categoría y beneficiario retornan resultados
- **AND** los gráficos de cashflow tienen datos de al menos 6 meses
