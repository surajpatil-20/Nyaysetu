import { apiRequest } from './client';

export const searchApi = {
  hybridSearch: async ({ q, court_id, case_type, year, document_type, top_k = 10, alpha = 0.5 }) => {
    const params = new URLSearchParams();
    if (q) params.append('q', q);
    if (court_id) params.append('court_id', court_id);
    if (case_type) params.append('case_type', case_type);
    if (year) params.append('year', year);
    if (document_type) params.append('document_type', document_type);
    if (top_k) params.append('top_k', top_k);
    if (alpha !== undefined) params.append('alpha', alpha);

    return apiRequest(`/api/search/?${params.toString()}`);
  },
};

