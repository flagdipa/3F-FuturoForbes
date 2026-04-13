# Concerns & Technical Debt

## Technical Debt
- **Mixed Languages**: UI templates use both English and Spanish keys/labels, causing occasional confusion in the `i18n.js` system.
- **Legacy Models**: References to "v1" models still exist in some parts of the code (`mapping_legacy_v2.md`).
- **SSE Stability**: Real-time updates via SSE sometimes fail or disconnect in long sessions.
- **Frontend State**: Alpine.js stores are growing large; some logic might benefit from being moved to dedicated service workers or a more robust state machine.

## Risks
- **Concurrency**: SQLite might face locking issues if the system scales to multiple simultaneous users writing frequently.
- **Data Integrity**: complex transaction splits require robust validation in `LedgerEngine` to prevent rounding errors or unbalanced entries.
- **Security**: Hardcoded configurations or default secrets in `.env.example` must be replaced in production.

## Future Improvements
- Migration to a fully decoupled frontend (e.g., Vite/React) if the Jinja2 complexity becomes unmanageable.
- Enhanced plugin isolation to prevent a faulty plugin from crashing the main process.
- Automated database backups and simplified restoration process.
