import { apiRequest } from './client';

export const authApi = {
  login: async (username, password) => {
    return apiRequest('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },

  register: async (userData) => {
    return apiRequest('/api/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  verifyOtp: async (email, otp) => {
    return apiRequest('/api/auth/verify-otp/', {
      method: 'POST',
      body: JSON.stringify({ email, otp }),
    });
  },

  resendOtp: async (email) => {
    return apiRequest('/api/auth/resend-otp/', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  getProfile: async () => {
    return apiRequest('/api/auth/me/');
  },

  refreshToken: async (refresh) => {
    return apiRequest('/api/auth/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh }),
    });
  },
};
