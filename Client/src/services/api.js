import axios from 'axios';

let rawApiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').trim();
if (!rawApiUrl.startsWith('http://') && !rawApiUrl.startsWith('https://')) {
  rawApiUrl = `https://${rawApiUrl}`;
}
const API_BASE_URL = rawApiUrl.endsWith('/api')
  ? rawApiUrl
  : `${rawApiUrl.replace(/\/+$/, '')}/api`;

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
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('tracelens_token');
        localStorage.removeItem('tracelens_user');
        localStorage.removeItem('tracelens_active_case');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
