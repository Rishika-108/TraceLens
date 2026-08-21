import api from './api';

export const caseService = {
  async getCases() {
    const response = await api.get('/cases/');
    return response.data;
  },

  async getCaseById(caseId) {
    const response = await api.get(`/cases/${caseId}`);
    return response.data;
  },

  async createCase(caseData) {
    const response = await api.post('/cases/', caseData);
    return response.data;
  },
};
