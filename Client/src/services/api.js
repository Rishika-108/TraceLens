import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Attach JWT bearer token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tracelens_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Global error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't auto-redirect if we're already on login page
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('tracelens_token');
        localStorage.removeItem('tracelens_user');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
