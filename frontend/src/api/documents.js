import { apiRequest } from './client';

export const documentsApi = {
  getUserDocuments: async () => {
    return apiRequest('/api/documents/user-documents/');
  },

  uploadDocument: async (file, title) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    else formData.append('title', file.name);

    return apiRequest('/api/documents/user-documents/', {
      method: 'POST',
      body: formData,
    });
  },

  getDocumentDetail: async (id) => {
    return apiRequest(`/api/documents/user-documents/${id}/`);
  },

  getDocumentSummary: async (id) => {
    return apiRequest(`/api/documents/user-documents/${id}/summary/`);
  },

  deleteDocument: async (id) => {
    return apiRequest(`/api/documents/user-documents/${id}/`, {
      method: 'DELETE',
    });
  },
};

