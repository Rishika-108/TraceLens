import React, { useState, useEffect } from 'react';
import { FiLayers, FiCode, FiClock, FiFileText, FiCpu, FiHash } from 'react-icons/fi';
import { Modal } from '../common/Modal';
import { StatBadge } from '../common/StatBadge';
import { evidenceService } from '../../services/evidence';

export const ArtifactViewer = ({ evidence, isOpen, onClose }) => {
  const [artifacts, setArtifacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedArtifact, setSelectedArtifact] = useState(null);

  useEffect(() => {
    if (isOpen && evidence?.id) {
      const fetchArtifacts = async () => {
        setLoading(true);
        try {
          const data = await evidenceService.getEvidenceArtifacts(evidence.id);
          setArtifacts(data);
          if (data.length > 0) setSelectedArtifact(data[0]);
        } catch (err) {
          console.error('Failed to fetch artifacts', err);
        } finally {
          setLoading(false);
        }
      };
      fetchArtifacts();
    } else {
      setArtifacts([]);
      setSelectedArtifact(null);
    }
  }, [isOpen, evidence]);

  if (!isOpen || !evidence) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2">
          <FiLayers className="text-cyan-400 w-5 h-5" />
          <span>Forensic Artifacts: {evidence.filename}</span>
        </div>
      }
      maxWidth="max-w-5xl"
    >
      <div className="text-left space-y-4">
        {/* Evidence Metadata Banner */}
        <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">FILE TYPE:</span>
            <span className="text-cyan-400 font-semibold">{evidence.file_type}</span>
          </div>
          <div>
            <span className="text-slate-500 block">STATUS:</span>
            <StatBadge status={evidence.status} size="sm" />
          </div>
          <div>
            <span className="text-slate-500 block">ARTIFACT COUNT:</span>
            <span className="text-slate-200 font-semibold">{artifacts.length} Items</span>
          </div>
          <div>
            <span className="text-slate-500 block">SHA-256 HASH:</span>
            <span className="text-slate-400 truncate block font-mono text-[10px]" title={evidence.file_hash}>
              {evidence.file_hash ? `${evidence.file_hash.slice(0, 12)}...` : 'N/A'}
            </span>
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs font-mono text-slate-400 animate-pulse">
            Loading forensic artifact records...
          </div>
        ) : artifacts.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-500">
            No parsed artifacts found for this evidence record.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            {/* Artifacts List Sidebar */}
            <div className="md:col-span-4 space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {artifacts.map((art, idx) => {
                const isSelected = selectedArtifact?.id === art.id;
                return (
                  <button
                    key={art.id}
                    onClick={() => setSelectedArtifact(art)}
                    className={`w-full p-3 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'bg-cyan-500/15 border-cyan-500/50 shadow-sm shadow-cyan-500/20'
                        : 'bg-slate-900/40 hover:bg-slate-900/80 border-slate-800/80'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[11px] font-mono font-semibold text-cyan-400">
                        #{idx + 1} • {art.artifact_type}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">
                        {art.timestamp ? new Date(art.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'No TS'}
                      </span>
                    </div>
                    <div className="text-xs text-slate-300 truncate">
                      {art.content ? Object.values(art.content).find((v) => typeof v === 'string') || 'Structured Record' : 'Artifact Record'}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Selected Artifact Deep Detail Viewer */}
            <div className="md:col-span-8 bg-slate-950/80 border border-slate-800 rounded-xl p-4 max-h-[500px] overflow-y-auto space-y-4">
              {selectedArtifact ? (
                <>
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <div className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                        <FiFileText className="text-cyan-400 w-4 h-4" />
                        {selectedArtifact.artifact_type} Record
                      </div>
                      <div className="text-[10px] font-mono text-slate-500 mt-0.5">
                        ID: {selectedArtifact.id}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/40 flex items-center gap-1">
                        <FiCpu className="w-3 h-3" />
                        Vector[384] Indexed
                      </span>
                    </div>
                  </div>

                  {/* Timestamp & Provenance Info */}
                  {selectedArtifact.timestamp && (
                    <div className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                      <FiClock className="text-cyan-400 w-3.5 h-3.5" />
                      Timestamp: {new Date(selectedArtifact.timestamp).toLocaleString()}
                    </div>
                  )}

                  {/* Structured Content JSON */}
                  <div>
                    <div className="text-[11px] font-mono font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
                      <FiCode className="text-cyan-400 w-3.5 h-3.5" />
                      STRUCTURED NORMALIZED CONTENT:
                    </div>
                    <pre className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-emerald-400 overflow-x-auto">
                      {JSON.stringify(selectedArtifact.content, null, 2)}
                    </pre>
                  </div>

                  {/* Raw Data Provenance Snippet */}
                  {selectedArtifact.raw_data && (
                    <div>
                      <div className="text-[11px] font-mono font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
                        <FiHash className="text-amber-400 w-3.5 h-3.5" />
                        ORIGINAL SOURCE SNIPPET:
                      </div>
                      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap">
                        {selectedArtifact.raw_data}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="py-16 text-center text-xs text-slate-500">
                  Select an artifact from the list to view forensic details.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
