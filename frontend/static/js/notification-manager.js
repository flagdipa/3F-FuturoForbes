/**
 * NotificationManager - Real-time notifications with SSE
 * Connects to backend SSE stream and displays toast notifications
 */
class NotificationManager {
    constructor() {
        this.eventSource = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds

        this.init();
    }

    /**
     * Initialize notification manager
     * Connect to SSE stream
     */
    init() {
        this.connect();

        // Reconnect on page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && !this.connected) {
                this.connect();
            }
        });
    }

    setupEventListeners() {
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearAll();
            });
        }
        this.markReadBtn = document.getElementById('mark-all-read-btn');
        if (this.markReadBtn) {
            this.markReadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markAllAsRead();
            });
        }
    }

    async loadHistory() {
        try {
            // Assuming 'api' is a globally available object for making API calls
            const response = await api.get('/notifications/');
            this.notifications = response.data;
            this.updateUI();
        } catch (error) {
            console.error('Error loading notification history:', error);
        }
    }

    updateUI() {
        if (!this.list) return;

        this.unreadCount = this.notifications.filter(n => !n.read).length;

        // Update badge
        if (this.badge) {
            if (this.unreadCount > 0) {
                this.badge.textContent = this.unreadCount;
                this.badge.style.display = 'inline-block';
            } else {
                this.badge.style.display = 'none';
            }
        }

        // Update count text
        if (this.countText) {
            this.countText.textContent = this.unreadCount;
        }

        // Update list
        if (this.notifications.length === 0) {
            this.list.innerHTML = `
                <div class="dropdown-item text-center text-dim py-5">
                    <i class="fa-solid fa-bell-slash fa-2x mb-2 opacity-25"></i>
                    <p class="mb-0">No hay notificaciones</p>
                </div>
            `;
            return;
        }

        this.list.innerHTML = this.notifications.map(n => {
            const timeStr = this.formatTime(n.timestamp);
            const iconClass = this.getIconClass(n.type);
            const textClass = n.read ? 'text-dim' : 'fw-bold';
            const bgClass = n.read ? '' : 'bg-secondary bg-opacity-10';

            return `
                <div class="dropdown-item p-3 border-bottom border-secondary border-opacity-10 ${bgClass}" 
                     style="white-space: normal; cursor: pointer;" 
                     onclick="notificationManager.markAsRead(${n.id}, '${n.action_url || ''}')">
                    <div class="d-flex align-items-start">
                        <div class="notification-icon rounded-circle p-2 me-3 ${n.type}">
                            <i class="fa-solid ${iconClass}"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <span class="small ${textClass}">${n.title}</span>
                                <span class="extra-small text-dim">${timeStr}</span>
                            </div>
                            <p class="mb-0 small text-dim line-clamp-2">${n.message}</p>
                            ${n.action_text ? `<span class="extra-small text-info mt-1 d-block font-orbitron">${n.action_text}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async markAsRead(id, redirectUrl) {
        try {
            // Assuming 'api' is a globally available object for making API calls
            await api.put(`/notifications/${id}/read`);
            // Update local state
            const notif = this.notifications.find(n => n.id === id);
            if (notif) notif.read = true;
            this.updateUI();

            if (redirectUrl) {
                window.location.href = redirectUrl;
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            await api.put('/notifications/read-all');
            this.notifications.forEach(n => n.read = true);
            this.updateUI();
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }

    async clearAll() {

        if (!confirm('¿Estás seguro de que deseas borrar todas las notificaciones?')) return;
        try {
            // Assuming 'api' is a globally available object for making API calls
            await api.delete('/notifications/');
            this.notifications = [];
            this.updateUI();
        } catch (error) {
            console.error('Error clearing notifications:', error);
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = (now - date) / 1000; // seconds

        if (diff < 60) return 'Ahora';
        if (diff < 3600) return `${Math.floor(diff / 60)}m`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
        return date.toLocaleDateString();
    }

    getIconClass(type) {
        const icons = {
            'success': 'fa-circle-check',
            'info': 'fa-circle-info',
            'warning': 'fa-triangle-exclamation',
            'error': 'fa-circle-xmark'
        };
        return icons[type] || 'fa-bell';
    }

    /**
     * Connect to SSE notification stream
     */
    connect() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        try {
            // Get JWT token for authentication
            const token = localStorage.getItem('token');
            if (!token) {
                console.warn('No auth token, skipping notification stream');
                return;
            }

            // Create SSE connection with auth header (via query param since EventSource doesn't support headers)
            this.eventSource = new EventSource(`/api/notifications/stream?token=${token}`);

            this.eventSource.onopen = () => {
                console.log('✅ Notification stream connected');
                this.connected = true;
                this.reconnectAttempts = 0;
            };

            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'connected') return;

                    // Handle regular notification
                    this.displayToast(data);

                    // Add to history list at the top
                    const newNotif = {
                        id: data.id_db,
                        type: data.type,
                        title: data.title,
                        message: data.message,
                        timestamp: data.timestamp,
                        read: false,
                        action_url: data.action_url,
                        action_text: data.action_text
                    };

                    this.notifications.unshift(newNotif);
                    this.updateUI();

                    // Trigger audio if permitted
                    this.playNotificationSound();

                } catch (error) {
                    console.error('Error parsing SSE message:', error);
                }
            };

            this.eventSource.onerror = (error) => {
                console.error('SSE connection error:', error);
                this.connected = false;
                this.eventSource.close();

                // Try to reconnect with exponential backoff
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
                    console.log(`Reconnecting in ${delay}ms...`);
                    setTimeout(() => this.connect(), delay);
                }
            };

        } catch (error) {
            console.error('Error connecting to notification stream:', error);
        }
    }

    /**
     * Display toast notification using existing logic
     */
    displayToast(data) {
        if (!data.title || !data.message) return;

        // Create container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const toastId = `toast-${Date.now()}`;
        const toastHtml = `
            <div id="${toastId}" class="toast custom-toast ${data.type}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-progress"></div>
                <div class="toast-header border-0 bg-transparent">
                    <div class="notification-icon rounded-circle p-2 me-2 ${data.type}">
                        <i class="fa-solid ${this.getIconClass(data.type)}"></i>
                    </div>
                    <strong class="me-auto font-orbitron text-uppercase small ls-1">${data.title}</strong>
                    <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body pt-0">
                    <p class="mb-2 small opacity-75">${data.message}</p>
                    ${data.action_url ? `
                        <div class="mt-2 text-end">
                            <a href="${data.action_url}" class="btn btn-xs btn-outline-light font-orbitron">${data.action_text || 'VER'}</a>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        // Assuming Bootstrap is available for toast functionality
        const bsToast = new bootstrap.Toast(toastElement, { delay: 5000 });
        bsToast.show();

        // Remove from DOM after hide
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    playNotificationSound() {
        // Implementation for sound could go here
        // For example:
        // const audio = new Audio('/static/sounds/notification.mp3');
        // audio.play().catch(e => console.warn("Notification sound failed to play:", e));
    }

    /**
     * Disconnect from stream
     */
    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.connected = false;
        }
    }
}

// Global instance
window.notificationManager = new NotificationManager();
