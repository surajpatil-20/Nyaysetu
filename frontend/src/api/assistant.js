import { apiRequest } from './client';

export const assistantApi = {
  askAssistant: async ({ query, court_id, case_type, year, top_k = 5, alpha = 0.5 }) => {
    return apiRequest('/api/assistant/', {
      method: 'POST',
      body: JSON.stringify({
        query,
        court_id: court_id ? parseInt(court_id) : undefined,
        case_type: case_type || undefined,
        year: year ? parseInt(year) : undefined,
        top_k,
        alpha,
      }),
    });
  },

  getAssistantInfo: async () => {
    return apiRequest('/api/assistant/');
  },
};

