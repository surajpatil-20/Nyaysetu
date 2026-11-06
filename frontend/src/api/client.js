/**
 * NYAYASETU Centralized API Client.
 * Automatically attaches JWT Bearer token and parses errors.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const token = localStorage.getItem('nyaysetu_access_token');
  const headers = {
    ...options.headers,
  };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Only set Content-Type for requests with a non-FormData body (avoids unnecessary preflight on GET)
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401 && token) {
    // If token expired, clear tokens
    localStorage.removeItem('nyaysetu_access_token');
    localStorage.removeItem('nyaysetu_refresh_token');
    localStorage.removeItem('nyaysetu_user');
  }

  if (response.status === 204) {
    return null;
  }

  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const errorMsg = data?.detail || data?.error || (typeof data === 'object' ? JSON.stringify(data) : 'An error occurred');
    const error = new Error(errorMsg);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

