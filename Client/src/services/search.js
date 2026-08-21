import api from './api';

export const searchService = {
  async semanticSearch(caseId, query, limit = 10) {
    const response = await api.post('/search/', {
      case_id: caseId,
      query,
      limit,
    });
    return response.data;
  },

  async investigateCase(caseId, question, limit = 8) {
    const response = await api.post('/investigations/', {
      case_id: caseId,
      question,
      limit,
    });
    return response.data;
  },
};
