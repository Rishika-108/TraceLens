import React, { useState } from 'react';
import {
  FiFileText,
  FiClock,
  FiLayers,
  FiZap,
  FiEye,
  FiShield,
} from 'react-icons/fi';
import { Modal } from '../common/Modal';

export const SearchResults = ({ results = [], query = '' }) => {
  const [selectedResult, setSelectedResult] = useState(null);

  if (!results || results.length === 0) {
    return (
      <div className="glass-panel p-12 rounded-2xl border border-dashed border-slate-800 text-center">
        <FiZap className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <div className="text-sm font-semibold text-slate-400">No matching evidence artifacts</div>
        <div className="text-xs text-slate-500 mt-1">
          {query ? `No evidence in vector space matched query "${query}".` : 'Enter a natural language search query above.'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 text-left">
      <div className="text-xs font-mono text-slate-400 mb-2 flex items-center justify-between">
        <span>RANKED EVIDENCE MATCHES ({results.length})</span>
        <span className="text-[10px] text-cyan-400">Vector Cosine Distance Scored</span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {results.map((item, idx) => {
          const scorePercent = Math.round((item.similarity_score || 0) * 100);
          const scoreColor =
            scorePercent > 80
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : scorePercent > 60
              ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
              : 'bg-slate-500/10 border-slate-500/30 text-slate-400';

          return (
            <div
              key={item.artifact_id || idx}
              className="glass-panel glass-panel-hover p-4 rounded-2xl border border-slate-800 flex flex-col justify-between group"
            >
              <div>
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${scoreColor}`}>
                      {scorePercent}% MATCH
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-300">
                      {item.artifact_type}
                    </span>
                  </div>

                  {item.timestamp && (
                    <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                      <FiClock className="w-3 h-3 text-slate-500" />
                      {new Date(item.timestamp).toLocaleString()}
                    </span>
                  )}
                </div>

                {/* Content snippet */}
                <div className="text-xs text-slate-200 line-clamp-3 font-normal leading-relaxed">
                  {item.content
                    ? Object.entries(item.content)
                        .filter(([k]) => !['file_path', 'raw'].includes(k))
                        .map(([k, v]) => `${k}: ${v}`)
                        .join(' | ')
                    : 'Structured Evidence Record'}
                </div>

                {item.raw_data && (
                  <div className="mt-2 p-2 rounded-lg bg-slate-950/80 border border-slate-800/80 text-[11px] font-mono text-slate-400 truncate">
                    Raw: {item.raw_data}
                  </div>
                )}
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-slate-500">
                <span>Art #{item.artifact_id?.slice(0, 8)} • Ev #{item.evidence_id?.slice(0, 8)}</span>
                <button
                  onClick={() => setSelectedResult(item)}
                  className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs font-sans font-medium flex items-center gap-1 transition-colors"
                >
                  <FiEye className="w-3 h-3" /> Inspect
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Inspect Modal */}
      {selectedResult && (
        <Modal
          isOpen={!!selectedResult}
          onClose={() => setSelectedResult(null)}
          title={
            <div className="flex items-center gap-2">
              <FiShield className="text-cyan-400 w-5 h-5" />
              <span>Evidence Match Inspection</span>
            </div>
          }
        >
          <div className="space-y-4 text-left font-mono text-xs">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 grid grid-cols-2 gap-2 text-[11px]">
              <div>
                <span className="text-slate-500 block">TYPE:</span>
                <span className="text-cyan-400 font-bold">{selectedResult.artifact_type}</span>
              </div>
              <div>
                <span className="text-slate-500 block">SIMILARITY:</span>
                <span className="text-emerald-400 font-bold">
                  {Math.round((selectedResult.similarity_score || 0) * 100)}%
                </span>
              </div>
            </div>

            <div>
              <span className="text-[11px] text-slate-400 block mb-1">NORMALIZED CONTENT:</span>
              <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-emerald-400 overflow-x-auto">
                {JSON.stringify(selectedResult.content, null, 2)}
              </pre>
            </div>

            {selectedResult.raw_data && (
              <div>
                <span className="text-[11px] text-slate-400 block mb-1">ORIGINAL RAW BYTES:</span>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 whitespace-pre-wrap">
                  {selectedResult.raw_data}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
