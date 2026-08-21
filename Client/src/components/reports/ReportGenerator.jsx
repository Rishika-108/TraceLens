import React, { useState } from 'react';
import {
  FiFileText,
  FiZap,
  FiCheckCircle,
  FiAlertTriangle,
  FiSliders,
  FiArrowRight,
} from 'react-icons/fi';
import { reportsService } from '../../services/reports';

export const ReportGenerator = ({ caseId, onReportGenerated }) => {
  const [customTitle, setCustomTitle] = useState('');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!caseId) return;
    setGenerating(true);
    setError(null);

    try {
      const report = await reportsService.generateReport(caseId, customTitle.trim() || null);
      setCustomTitle('');
      if (onReportGenerated) onReportGenerated(report);
    } catch (err) {
      console.error('Report generation failed', err);
      setError(err.response?.data?.detail || 'Failed to synthesize case intelligence report.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 text-left space-y-4">
      <div>
        <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
          <FiFileText className="text-cyan-400 w-5 h-5" />
          Synthesize Case Intelligence Report
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Orchestrates the Report Agent to compile structured case metrics, chronological timelines, entity directories, and executive findings.
        </p>
      </div>

      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <label className="block text-xs font-mono font-medium text-slate-400 mb-1.5">
            CUSTOM REPORT TITLE (OPTIONAL)
          </label>
          <input
            type="text"
            value={customTitle}
            onChange={(e) => setCustomTitle(e.target.value)}
            placeholder="e.g. Official Case Assessment: Operation Sovereign Vault"
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-2.5 px-3.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <FiAlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={generating}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs tracking-wide shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            <FiZap className="w-4 h-4" />
            <span>{generating ? 'Synthesizing Intelligence...' : 'Generate Case Report'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
