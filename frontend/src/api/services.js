import { apiRequest } from './client';

export const servicesApi = {
  getServices: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/services/services/${query ? `?${query}` : ''}`);
  },
};

