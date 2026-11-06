import { apiRequest } from './client';

export const graphApi = {
  getCaseGraph: async (caseId) => {
    return apiRequest(`/api/graph/cases/${caseId}/`);
  },

  getGraphStatus: async () => {
    return apiRequest('/api/graph/status/');
  },
};

