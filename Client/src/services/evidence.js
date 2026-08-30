import api from './api';

export const evidenceService = {
  async uploadEvidence(caseId, file, fileType = null, onUploadProgress = null) {
    const formData = new FormData();
    formData.append('case_id', caseId);
    formData.append('file', file);
    if (fileType) {
      formData.append('file_type', fileType);
    }

    const response = await api.post('/evidence/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  async getEvidenceByCase(caseId) {
    const response = await api.get(`/evidence/case/${caseId}`);
    return response.data;
  },

  async getEvidenceById(evidenceId) {
    const response = await api.get(`/evidence/${evidenceId}`);
    return response.data;
  },

  async getEvidenceArtifacts(evidenceId) {
    const response = await api.get(`/evidence/${evidenceId}/artifacts`);
    return response.data;
  },

  async deleteEvidence(evidenceId) {
    const response = await api.delete(`/evidence/${evidenceId}`);
    return response.data;
  },

  async reprocessEvidence(evidenceId) {
    const response = await api.post(`/evidence/${evidenceId}/reprocess`);
    return response.data;
  },
};
