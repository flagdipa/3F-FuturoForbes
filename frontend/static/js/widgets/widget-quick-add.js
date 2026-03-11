/**
 * Widget: Quick Add
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetQuickAdd() {
    const def = () => ({
        openForm(type) {
            window.dispatchEvent(new CustomEvent('open-transaction-form', {
                detail: { type: type }
            }));
        }
    });

    if (typeof Alpine !== 'undefined' && Alpine.data) {
        Alpine.data('widgetQuickAdd', def);
    } else {
        document.addEventListener('alpine:init', () => Alpine.data('widgetQuickAdd', def));
    }
})();
