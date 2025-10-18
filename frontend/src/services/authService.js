/**
 * Authentication Service
 */

import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

const authService = {
  /**
   * Login with email and password
   */
  login: async (email, password) => {
    try {
      const response = await axios.post(API_ENDPOINTS.LOGIN, {
        email,
        password,
      });
      
      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Register a new user
   */
  register: async (userData) => {
    try {
      const response = await axios.post(API_ENDPOINTS.REGISTER, userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * Logout
   */
  logout: async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await axios.post(API_ENDPOINTS.LOGOUT, {}, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Get current user
   */
  getCurrentUser: async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return null;
      }

      const response = await axios.get(API_ENDPOINTS.ME, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response.data;
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      return null;
    }
  },

  /**
   * Refresh access token
   */
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        return null;
      }

      const response = await axios.post(API_ENDPOINTS.REFRESH, {
        refresh: refreshToken,
      });

      if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
      }

      return response.data;
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      return null;
    }
  },

  /**
   * Get authorization header
   */
  getAuthHeader: () => {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

export default authService;

