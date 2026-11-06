import { apiRequest } from './client';

export const casesApi = {
  getCases: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`/api/cases/cases/${query ? `?${query}` : ''}`);
  },

  getCaseDetail: async (id) => {
    return apiRequest(`/api/cases/cases/${id}/`);
  },

  getRelatedCases: async (id) => {
    return apiRequest(`/api/cases/${id}/related/`);
  },

  getCaseTimeline: async (id) => {
    return apiRequest(`/api/search/cases/${id}/timeline/`);
  },
};

