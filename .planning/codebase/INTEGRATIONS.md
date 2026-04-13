# Integrations

## External Services
- **Gravatar**: Used for user profile images (based on email).
- **CDN Dependencies**:
  - Google Fonts (Inter, Orbitron)
  - FontAwesome (cdnjs)
  - AdminLTE (jsdelivr)
  - Alpine.js (unpkg)
  - Axios (jsdelivr)
  - SweetAlert2 (jsdelivr)
  - SortableJS (cdnjs)
  - Bootstrap (jsdelivr)

## Internal Integrations
- **Plugin System**: Modular architecture inspired by PrestaShop, allowing dynamic activation of "hooks" and module injection.
- **REST API**: Internal communication via `/api/v1` endpoints using JSON.
- **SSE (Server-Sent Events)**: (Found in `main.py` context or history) Used for real-time updates (e.g., categories manager, notifications).
- **Filesystem**: Local storage for "Vault" attachments.
