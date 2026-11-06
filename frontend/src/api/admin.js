import { apiRequest } from './client';

export const adminApi = {
  getStats: async () => {
    return apiRequest('/api/admin/stats/');
  },
};

