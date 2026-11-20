import { apiRequest } from './client';

export const lawsApi = {
  getCategories: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/laws/categories/${query ? `?${query}` : ''}`);
  },

  getScenarios: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/laws/scenarios/${query ? `?${query}` : ''}`);
  },

  getScenarioDetail: async (id) => {
    return apiRequest(`/api/laws/scenarios/${id}/`);
  },

  getActs: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/laws/acts/${query ? `?${query}` : ''}`);
  },
};
