/**
 * 3F System - Main JS Foundation
 * Handles Auth, Theme interactions, and common utilities
 */

const api = axios.create({
    baseURL: '/api',
    timeout: 10000,
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
    console.log('3F System initialized - Welcome to the Future.');
    checkAuth();
});

async function checkAuth() {
    const token = localStorage.getItem('3f_token');
    const emailSpan = document.getElementById('user-email');

    if (!token && window.location.pathname !== '/login') {
        window.location.href = '/login';
        return;
    }

    if (token && emailSpan) {
        // En un futuro aquí pediremos los datos del usuario actual
        emailSpan.innerText = 'Explorador 3F';
    }
}
