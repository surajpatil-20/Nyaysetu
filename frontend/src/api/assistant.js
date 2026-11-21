import { apiRequest } from './client';

export const assistantApi = {
  askAssistant: async ({ query, case_id, court_id, case_type, year, top_k = 5, alpha = 0.5 }) => {
    return apiRequest('/api/assistant/', {
      method: 'POST',
      body: JSON.stringify({
        query,
        case_id: case_id ? parseInt(case_id, 10) : undefined,
        court_id: court_id ? parseInt(court_id, 10) : undefined,
        case_type: case_type || undefined,
        year: year ? parseInt(year, 10) : undefined,
        top_k,
        alpha,
      }),
    });
  },

  getAssistantInfo: async () => {
    return apiRequest('/api/assistant/');
  },
};

