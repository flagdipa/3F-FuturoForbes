/**
 * Widget: Quick Add
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('widgetQuickAdd', () => ({
        openForm(type) {
            window.dispatchEvent(new CustomEvent('open-transaction-form', {
                detail: { type: type }
            }));
        }
    }));
});
