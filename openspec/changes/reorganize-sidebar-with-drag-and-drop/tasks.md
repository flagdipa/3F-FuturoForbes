# Implementation Tasks

## 1. Backend: Preferences Endpoint
- [x] 1.1 Integrate a fast way to retrieve and update user UI settings (specifically the sidebar sections order). This can be a new API route `GET/PUT /api/v1/users/me/preferences` backing into `SystemConfig` or `CustomFieldValue`.

## 2. Frontend: Sidebar State & API Integration
- [x] 2.1 Update `sidebar-manager.js` to fetch and store `menuStructure` preferences upon initialization, providing a fallback default array if none exists.
- [x] 2.2 Update account parsing logic in `sidebar-manager.js` to group the loaded accounts by type (e.g., Banks, Wallets, Cash, Credit Cards) instead of just filtering them into ARS/USD flat lists.

## 3. Frontend: Dynamic Sidebar Render
- [x] 3.1 Refactor `frontend/templates/modules/sidebar.html` to remove static blocks (Dashboard, Planificación, etc.) and instead iterate over the `menuStructure` array using Alpine.js `<template x-for>`.
- [x] 3.2 Update `sidebar.html` to render the newly grouped account arrays under their respective dynamic categories.
- [x] 3.3 Implement a `<template x-for>` block specifically for active plugins under the "Módulos" section, iterating `Alpine.store('sidebar').activePlugins`.

## 4. Frontend: Drag and Drop (SortableJS)
- [x] 4.1 Initialize `Sortable` on the main sidebar menu `<ul>` or wrap the draggable sections in a specific container, likely in a `$nextTick` after Alpine's setup.
- [x] 4.2 Add an `onEnd` event listener to SortableJS to capture the newly sorted sequence of items.
- [x] 4.3 In the `onEnd` handler, serialize the new order and trigger the API `PUT` request to permanently save the user's sidebar preference.
