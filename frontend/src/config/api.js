/**
 * API Configuration
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: `${API_BASE_URL}/auth/login/`,
  LOGOUT: `${API_BASE_URL}/auth/logout/`,
  REFRESH: `${API_BASE_URL}/auth/refresh/`,
  ME: `${API_BASE_URL}/auth/me/`,
  REGISTER: `${API_BASE_URL}/auth/register/`,

  // Clients
  CLIENTS: `${API_BASE_URL}/clients/`,
  CLIENT_DETAIL: (id) => `${API_BASE_URL}/clients/${id}/`,
  CLIENT_CONTACTS: (id) => `${API_BASE_URL}/clients/${id}/contacts/`,
  CLIENT_HISTORY: (id) => `${API_BASE_URL}/clients/${id}/history/`,

  // Quotes
  QUOTES: `${API_BASE_URL}/quotes/`,
  QUOTE_DETAIL: (id) => `${API_BASE_URL}/quotes/${id}/`,
  QUOTE_SEND: (id) => `${API_BASE_URL}/quotes/${id}/send/`,
  QUOTE_APPROVE: (id) => `${API_BASE_URL}/quotes/${id}/approve/`,
  QUOTE_REJECT: (id) => `${API_BASE_URL}/quotes/${id}/reject/`,
  QUOTE_HISTORY: (id) => `${API_BASE_URL}/quotes/${id}/history/`,

  // Services
  SERVICES: `${API_BASE_URL}/services/`,
  SERVICE_DETAIL: (id) => `${API_BASE_URL}/services/${id}/`,

  // Analytics
  ANALYTICS_DASHBOARD: `${API_BASE_URL}/analytics/dashboard/`,
  ANALYTICS_CLIENTS: `${API_BASE_URL}/analytics/clients/`,
  ANALYTICS_QUOTES: `${API_BASE_URL}/analytics/quotes/`,
};

export default API_BASE_URL;

