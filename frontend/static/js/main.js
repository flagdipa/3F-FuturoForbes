/**
 * 3F System - Main JS Foundation
 * Handles Auth, Theme interactions, and common utilities
 */

const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
});
window.api = api;

// Interceptor para incluir Token en cada petición
api.interceptors.request.use(config => {
    const token = localStorage.getItem('3f_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Interceptor para manejar errores globales (ej: 401 Unauthorized)
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('3f_token');
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

async function checkAuth() {
    const token = localStorage.getItem('3f_token');
    const emailSpan = document.getElementById('user-email');

    if (!token && window.location.pathname !== '/login') {
        window.location.href = '/login';
        return;
    }

    if (token) {
        console.log('Token found, fetching profile...');
        try {
            const res = await api.get('/auth/profile');
            console.log('Profile fetched:', res.data);
            const userData = res.data;
            if (emailSpan) emailSpan.innerText = userData.email;
            
            const nameEl = document.getElementById('header-user-name');
            if (nameEl) nameEl.innerText = userData.full_name || userData.email;
            
            const dashNameEl = document.getElementById('dash-user-name');
            if (dashNameEl) dashNameEl.innerText = userData.full_name || userData.email;
            
            // Sync with avatars
            const avatars = document.querySelectorAll('.user-menu img, .user-header img');
            const displayName = userData.full_name || userData.email.split('@')[0];
            avatars.forEach(img => {
                img.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=00f2ff&color=000`;
            });
        } catch (e) {
            console.error('Error fetching profile:', e);
        }
    }
}

window.logout = function () {
    localStorage.removeItem('3f_token');
    window.location.href = '/login';
};

// Session Timeout Logic
let idleTimer;
const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

function resetIdleTimer() {
    const timeoutMinutes = parseInt(localStorage.getItem('3f_session_timeout') || '0');
    if (timeoutMinutes <= 0) return; // Disabled

    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
        console.warn('Session timed out due to inactivity.');
        window.logout();
    }, timeoutMinutes * 60 * 1000);
}

// Initialize Timer
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    // Check if timeout is enabled and set up listeners
    const timeoutMinutes = parseInt(localStorage.getItem('3f_session_timeout') || '0');
    if (timeoutMinutes > 0) {
        events.forEach(event => {
            document.addEventListener(event, resetIdleTimer, true);
        });
        resetIdleTimer(); // Start timer immediately
    }
});

