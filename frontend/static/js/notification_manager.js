/**
 * Global Notification Manager for 3F Project
 * Provides a unified way to show toasts and alerts.
 */
window.NotificationManager = {
    /**
     * Show a toast message
     * @param {string} message 
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {string} title 
     */
    show: function(message, type = 'info', title = '') {
        // Fallback to alert if Swal is not loaded
        if (typeof Swal === 'undefined') {
            alert((title ? title + ': ' : '') + message);
            return;
        }

        const icons = {
            success: 'success',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };

        const config = {
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            icon: icons[type] || 'info',
            title: title || '',
            text: message,
            background: 'rgba(7, 30, 38, 0.95)',
            color: '#fff',
            iconColor: type === 'error' ? '#ff3e3e' : (type === 'success' ? '#00f0ff' : '#ffac2d'),
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        };

        Swal.fire(config);
    },

    success: function(msg, title = '') { this.show(msg, 'success', title); },
    error: function(msg, title = '') { this.show(msg, 'error', title); },
    warning: function(msg, title = '') { this.show(msg, 'warning', title); },
    info: function(msg, title = '') { this.show(msg, 'info', title); },

    /**
     * Show a confirmation dialog
     * @param {string} message 
     * @param {string} title 
     */
    confirm: async function(message, title = 'Confirmar') {
        if (typeof Swal === 'undefined') {
            return confirm(message);
        }

        const result = await Swal.fire({
            title: title,
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#00f0ff',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar',
            background: 'rgba(7, 30, 38, 0.95)',
            color: '#fff'
        });

        return result.isConfirmed;
    }
};
