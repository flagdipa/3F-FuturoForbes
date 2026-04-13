# Coding Conventions

## Python (Backend)
- **Style**: PEP 8 compliant.
- **Naming**: 
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Imports**: Alphabetical order within groups (stdlib, third-party, local).
- **Models**: Use SQLModel for all database-backed entities.
- **Type Hinting**: Mandatory for all function signatures.

## JavaScript (Frontend)
- **Naming**: `camelCase` for functions and variables.
- **Logic**: Use Alpine.js `$store` for shared state management.
- **API Calls**: Always use `axios`. Handle errors with `sweetalert2`.
- **Modularity**: Logic divided into "Managers" (e.g., `sidebar-manager.js`, `category-manager.js`).

## HTML/Templates
- **Naming**: `snake_case` for template filenames (e.g., `base_layout.html`).
- **Structure**: Use Jinja2 `{% block %}` for extensibility.
- **Styling**: Prefer AdminLTE/Bootstrap classes; use custom Neon variables for color consistency.

## Git
- **Commit Messages**: Present tense, descriptive (e.g., "Add category filtering to sidebar").
- **Branching**: Use feature branches if applicable.
