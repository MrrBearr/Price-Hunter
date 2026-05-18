import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `${window.location.origin}/_/backend` : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth
export const authAPI = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/api/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
};

// Search
export const searchAPI = {
  search: (params: { q: string; category?: string; min_price?: number; max_price?: number; sort_by?: string; page?: number }) =>
    api.get('/api/search', { params }),
  trigger: (q: string) =>
    api.post(`/api/search/trigger?q=${encodeURIComponent(q)}`),
};

// Products
export const productsAPI = {
  getAll: (params?: { page?: number; per_page?: number; category?: string }) =>
    api.get('/api/products', { params }),
  getById: (id: string) =>
    api.get(`/api/products/${id}`),
  getHistory: (id: string, days?: number) =>
    api.get(`/api/products/${id}/history`, { params: { days } }),
};

// Offers
export const offersAPI = {
  getByProduct: (productId: string, sort_by?: string) =>
    api.get(`/api/offers/product/${productId}`, { params: { sort_by } }),
  getById: (id: string) =>
    api.get(`/api/offers/${id}`),
};

// Coupons
export const couponsAPI = {
  getAll: (params?: { store_id?: string; active_only?: boolean; page?: number }) =>
    api.get('/api/coupons', { params }),
  create: (data: any) =>
    api.post('/api/coupons', data),
  test: (couponId: string) =>
    api.post(`/api/coupons/${couponId}/test`),
  getTests: (couponId: string) =>
    api.get(`/api/coupons/${couponId}/tests`),
};

// Favorites
export const favoritesAPI = {
  getAll: () => api.get('/api/favorites'),
  add: (productId: string) =>
    api.post('/api/favorites', { product_id: productId }),
  remove: (productId: string) =>
    api.delete(`/api/favorites/${productId}`),
};

// Alerts
export const alertsAPI = {
  getAll: () => api.get('/api/alerts'),
  create: (data: { product_id: string; target_price: number }) =>
    api.post('/api/alerts', data),
  delete: (alertId: string) =>
    api.delete(`/api/alerts/${alertId}`),
};
