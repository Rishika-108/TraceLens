import React, { useState, useEffect } from 'react';
import {
  FiFileText,
  FiClock,
  FiRefreshCw,
  FiArchive,
  FiCheckCircle,
} from 'react-icons/fi';
import { useCase } from '../context/CaseContext';
import { ReportGenerator } from '../components/reports/ReportGenerator';
import { ReportViewer } from '../components/reports/ReportViewer';
import { reportsService } from '../services/reports';

export const Report = () => {
  const { activeCase } = useCase();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await reportsService.getReportsByCase(activeCase.id);
      setReports(data);
      if (data.length > 0) {
        setSelectedReport(data[0]);
      } else {
        setSelectedReport(null);
      }
    } catch (err) {
      console.error('Failed to load reports', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [activeCase]);

  const handleReportGenerated = (newReport) => {
    setReports((prev) => [newReport, ...prev]);
    setSelectedReport(newReport);
  };

  if (!activeCase) {
    return (
      <div className="py-24 text-center max-w-md mx-auto">
        <FiFileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-slate-200">No Target Case Selected</h3>
        <p className="text-xs text-slate-500 mt-1">
          Please select an active case from the top navigation dropdown or portfolio dashboard.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-left max-w-7xl mx-auto p-2">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest mb-1.5">
            <FiFileText className="w-4 h-4" />
            <span>Forensic Intelligence Output</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Case Intelligence Report Studio
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Synthesize multi-source digital evidence into comprehensive, auditable forensic reports with verifiable provenance.
          </p>
        </div>

        <button
          onClick={fetchReports}
          disabled={loading}
          className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-colors shrink-0"
          title="Refresh Reports Archive"
        >
          <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>

      {/* Generator Box */}
      <ReportGenerator
        caseId={activeCase.id}
        onReportGenerated={handleReportGenerated}
      />

      {/* Reports Grid / Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Historical Reports Archive Sidebar */}
        <div className="lg:col-span-4 glass-panel p-5 rounded-2xl border border-slate-800 h-fit space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h4 className="text-xs font-mono font-semibold uppercase text-slate-400 flex items-center gap-1.5">
              <FiArchive className="text-cyan-400 w-3.5 h-3.5" />
              Archived Reports ({reports.length})
            </h4>
          </div>

          {loading && reports.length === 0 ? (
            <div className="py-8 text-center text-xs font-mono text-slate-500 animate-pulse">
              Loading report archive...
            </div>
          ) : reports.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">
              No reports generated for this case yet.
            </div>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {reports.map((rep) => {
                const isSelected = selectedReport?.id === rep.id;
                return (
                  <button
                    key={rep.id}
                    onClick={() => setSelectedReport(rep)}
                    className={`w-full p-3.5 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'bg-cyan-500/15 border-cyan-500/50 shadow-sm shadow-cyan-500/10'
                        : 'bg-slate-900/40 hover:bg-slate-900/80 border-slate-800/80'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 mb-1">
                      <span className="text-cyan-400 font-semibold">REPORT</span>
                      <span>
                        {rep.created_at ? new Date(rep.created_at).toLocaleDateString() : 'Recent'}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-slate-200 truncate">{rep.title}</div>
                    <div className="text-[11px] text-slate-400 line-clamp-2 mt-1">
                      {rep.summary}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Selected Report Viewer Canvas */}
        <div className="lg:col-span-8">
          <ReportViewer report={selectedReport} />
        </div>
      </div>
    </div>
  );
};
