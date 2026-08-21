import api from './api';

export const intelligenceService = {
  async getTimelineByCase(caseId) {
    const response = await api.get(`/timelines/case/${caseId}`);
    return response.data;
  },

  async getEntitiesByCase(caseId) {
    const response = await api.get(`/entities/case/${caseId}`);
    return response.data;
  },

  async getRelationshipsByCase(caseId) {
    const response = await api.get(`/relationships/case/${caseId}`);
    return response.data;
  },
};
