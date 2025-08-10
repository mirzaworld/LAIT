import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || localStorage.getItem('lait_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for auth + error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // Token invalid/expired -> logout flow placeholder
        localStorage.removeItem('token');
        localStorage.removeItem('lait_token');
        // Optionally trigger a redirect event
        window.dispatchEvent(new CustomEvent('auth-expired'));
      }
      console.error('API error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Network error: no response received');
    } else {
      console.error('Axios error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
