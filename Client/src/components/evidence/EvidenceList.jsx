import React, { useState, useEffect } from 'react';
import {
  FiFile,
  FiLayers,
  FiCopy,
  FiCheck,
  FiRefreshCw,
  FiHardDrive,
  FiShield,
} from 'react-icons/fi';
import { StatBadge } from '../common/StatBadge';
import { ArtifactViewer } from './ArtifactViewer';
import { evidenceService } from '../../services/evidence';

export const EvidenceList = ({ caseId, refreshTrigger }) => {
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [copiedHash, setCopiedHash] = useState(null);

  const fetchEvidence = async () => {
    if (!caseId) return;
    setLoading(true);
    try {
      const data = await evidenceService.getEvidenceByCase(caseId);
      setEvidenceList(data);
    } catch (err) {
      console.error('Failed to fetch evidence list', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [caseId, refreshTrigger]);

  const copyToClipboard = (hash) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const handleInspect = (item) => {
    setSelectedEvidence(item);
    setIsViewerOpen(true);
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 text-left">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <FiHardDrive className="text-cyan-400 w-5 h-5" />
            Case Evidence Inventory ({evidenceList.length})
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Cryptographically sealed forensic repository for chain of custody.
          </p>
        </div>
        <button
          onClick={fetchEvidence}
          disabled={loading}
          className="p-2 rounded-xl bg-slate-900/60 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-all"
          title="Refresh Evidence List"
        >
          <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>

      {loading && evidenceList.length === 0 ? (
        <div className="py-12 text-center text-xs font-mono text-slate-400 animate-pulse">
          Querying secure evidence store...
        </div>
      ) : evidenceList.length === 0 ? (
        <div className="py-12 text-center border border-dashed border-slate-800 rounded-xl">
          <FiFile className="w-8 h-8 text-slate-600 mx-auto mb-2" />
          <div className="text-sm font-semibold text-slate-400">No evidence records ingested yet</div>
          <div className="text-xs text-slate-500 mt-1">
            Upload chat transcripts, call records, emails, or databases above to begin forensic extraction.
          </div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-3">File / Evidence</th>
                <th className="py-3 px-3">Category</th>
                <th className="py-3 px-3">Size</th>
                <th className="py-3 px-3">SHA-256 Hash</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {evidenceList.map((item) => (
                <tr key={item.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3.5 px-3">
                    <div className="font-semibold text-slate-200 flex items-center gap-2">
                      <FiFile className="text-cyan-400 shrink-0 w-4 h-4" />
                      <span className="truncate max-w-[200px]" title={item.filename}>
                        {item.filename}
                      </span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500 mt-0.5 truncate max-w-[200px]">
                      {item.id}
                    </div>
                  </td>
                  <td className="py-3.5 px-3 font-mono text-slate-300">
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px]">
                      {item.file_type}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 font-mono text-slate-400">
                    {formatBytes(item.file_size)}
                  </td>
                  <td className="py-3.5 px-3 font-mono text-slate-400">
                    {item.file_hash ? (
                      <div className="flex items-center gap-1.5">
                        <span className="truncate max-w-[120px]" title={item.file_hash}>
                          {item.file_hash.slice(0, 10)}...{item.file_hash.slice(-6)}
                        </span>
                        <button
                          onClick={() => copyToClipboard(item.file_hash)}
                          title="Copy Full SHA-256 Hash"
                          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition-colors"
                        >
                          {copiedHash === item.file_hash ? (
                            <FiCheck className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <FiCopy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    ) : (
                      <span className="text-slate-600">Pending</span>
                    )}
                  </td>
                  <td className="py-3.5 px-3">
                    <StatBadge status={item.status} size="sm" />
                  </td>
                  <td className="py-3.5 px-3 text-right">
                    <button
                      onClick={() => handleInspect(item)}
                      className="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 font-medium text-xs transition-all flex items-center gap-1.5 ml-auto"
                    >
                      <FiLayers className="w-3.5 h-3.5" />
                      Artifacts
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Artifact Deep Inspection Modal */}
      <ArtifactViewer
        evidence={selectedEvidence}
        isOpen={isViewerOpen}
        onClose={() => {
          setIsViewerOpen(false);
          setSelectedEvidence(null);
        }}
      />
    </div>
  );
};
