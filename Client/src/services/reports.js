import api from './api';

export const reportsService = {
  async generateReport(caseId, title = null) {
    const params = { case_id: caseId };
    if (title) params.title = title;
    const response = await api.post('/reports/generate', null, { params });
    return response.data;
  },

  async getReportsByCase(caseId) {
    const response = await api.get(`/reports/case/${caseId}`);
    return response.data;
  },

  async getReportById(reportId) {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
  },
};
