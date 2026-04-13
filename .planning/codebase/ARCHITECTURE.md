# Architecture

## Core Design Principles
- **Monolith with Plugin Support**: The main system is a FastAPI monolith, but it supports independent plugins that can register hooks.
- **Micro-Frontend with Alpine.js**: Reactive UI logic is localized in HTML templates using Alpine.js and global stores (`x-data`, `$store`).
- **Double-Entry Accounting**: Financial transactions are stored as `Transaction` records with multiple `TransactionSplit` records ensuring balance.
- **Soft Deletion**: Most entities use `SoftDeleteMixin` to avoid permanent data loss.
- **Audit Logging**: Actions are tracked via `AuditMixin` and `AuditLog` table.

## Data Flow
1. **Request**: Browser sends request (Standard HTML or Axios JSON).
2. **Routing**: `ui_router` handles page rendering; `v1_router` handles API logic.
3. **Controller/Logic**: Backend logic interacts with SQLModel models.
4. **Persistence**: Changes saved to SQLite/Postgres.
5. **Real-time**: SSE endpoints notify the frontend of changes (e.g., category updates).

## Key Components
- **LedgerEngine**: (Found in code history) Handles the calculation of balances and transaction integrity.
- **PluginManager**: Manages installation, activation, and hook execution for modules.
- **Vault**: Logical directory structure mapped to physical files for attachments.
