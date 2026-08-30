import React from 'react';
import {
  FiFileText,
  FiPrinter,
  FiClock,
  FiShield,
  FiUsers,
  FiShare2,
  FiHardDrive,
} from 'react-icons/fi';

export const ReportViewer = ({ report }) => {
  if (!report) {
    return (
      <div className="glass-panel p-16 rounded-2xl border border-dashed border-slate-800 text-center">
        <FiFileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <h4 className="text-base font-semibold text-slate-300">No report selected</h4>
        <p className="text-xs text-slate-500 mt-1">
          Select an archived report or generate a new intelligence assessment above.
        </p>
      </div>
    );
  }

  const metrics = report.evidence?.metrics || {};
  const narrative = report.evidence?.narrative_report || report.summary || '';

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="glass-panel p-8 rounded-3xl border border-slate-800 text-left space-y-6 print:border-none print:p-0 print:bg-white print:text-black">
      {/* Report Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6 print:border-black">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest mb-1 print:text-black">
            <FiShield className="w-4 h-4" />
            Official Digital Forensics Case Report
          </div>
          <h2 className="text-2xl font-bold text-slate-100 print:text-black">{report.title}</h2>
          <div className="text-xs font-mono text-slate-500 mt-1 flex items-center gap-3 print:text-black">
            <span>Report ID: {report.id}</span>
            <span>•</span>
            <span>Case ID: {report.case_id}</span>
            <span>•</span>
            <span>
              Generated:{' '}
              {report.created_at ? new Date(report.created_at).toLocaleString() : 'Recent'}
            </span>
          </div>
        </div>

        <button
          onClick={handlePrint}
          className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold flex items-center gap-2 transition-colors shrink-0 print:hidden"
        >
          <FiPrinter className="w-4 h-4" />
          Print / Export PDF
        </button>
      </div>

      {/* Structured Metrics Banner */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs font-mono print:bg-slate-100 print:border-black">
          <div className="p-2">
            <span className="text-slate-500 block text-[10px]">SOURCE EVIDENCE:</span>
            <span className="text-cyan-400 font-bold text-base print:text-black">
              {metrics.evidence_count || 0} Files
            </span>
          </div>
          <div className="p-2">
            <span className="text-slate-500 block text-[10px]">PARSED ARTIFACTS:</span>
            <span className="text-indigo-400 font-bold text-base print:text-black">
              {metrics.artifacts_count || 0} Records
            </span>
          </div>
          <div className="p-2">
            <span className="text-slate-500 block text-[10px]">TIMELINE EVENTS:</span>
            <span className="text-emerald-400 font-bold text-base print:text-black">
              {metrics.timeline_events_count || 0} Events
            </span>
          </div>
          <div className="p-2">
            <span className="text-slate-500 block text-[10px]">DISCOVERED ENTITIES:</span>
            <span className="text-amber-400 font-bold text-base print:text-black">
              {metrics.entities_count || 0} Unique
            </span>
            {metrics.total_entity_mentions && metrics.total_entity_mentions > metrics.entities_count ? (
              <span className="text-slate-500 text-[10px] block font-mono">
                ({metrics.total_entity_mentions} mentions)
              </span>
            ) : null}
          </div>
          <div className="p-2">
            <span className="text-slate-500 block text-[10px]">RELATIONSHIPS:</span>
            <span className="text-violet-400 font-bold text-base print:text-black">
              {metrics.relationships_count || 0} Links
            </span>
          </div>
        </div>
      )}

      {/* Narrative Report Content */}
      <div className="p-6 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-slate-200 text-xs leading-relaxed space-y-4 print:bg-white print:border-none print:text-black font-sans">
        {narrative.split('\n').map((line, idx) => {
          if (line.startsWith('# ')) {
            return (
              <h2 key={idx} className="text-xl font-bold text-cyan-400 mt-6 mb-3 print:text-black">
                {line.replace('# ', '')}
              </h2>
            );
          }
          if (line.startsWith('## ')) {
            return (
              <h3
                key={idx}
                className="text-base font-bold text-slate-100 mt-5 mb-2 border-b border-slate-800 pb-1.5 print:text-black print:border-black"
              >
                {line.replace('## ', '')}
              </h3>
            );
          }
          if (line.startsWith('- ')) {
            return (
              <li key={idx} className="ml-4 list-disc text-slate-300 print:text-black my-1">
                {line.replace('- ', '')}
              </li>
            );
          }
          if (!line.trim()) return <div key={idx} className="h-2" />;
          return (
            <p key={idx} className="text-slate-300 print:text-black">
              {line}
            </p>
          );
        })}
      </div>
    </div>
  );
};
