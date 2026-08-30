import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FiFolderPlus,
  FiFolder,
  FiHardDrive,
  FiActivity,
  FiSearch,
  FiArrowRight,
  FiClock,
  FiCheckCircle,
} from 'react-icons/fi';
import { Modal } from '../components/common/Modal';
import { useCase } from '../context/CaseContext';

export const Dashboard = () => {
  const { cases, selectCase, createNewCase, loading } = useCase();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  const handleCreateCase = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    try {
      const newCase = await createNewCase({ title, description });
      setIsModalOpen(false);
      setTitle('');
      setDescription('');
      selectCase(newCase);
      navigate('/case');
    } catch (err) {
      console.error('Failed to create case', err);
    } finally {
      setCreating(false);
    }
  };

  const handleSelectCase = (caseObj) => {
    selectCase(caseObj);
    navigate('/case');
  };

  return (
    <div className="space-y-8 text-left max-w-7xl mx-auto p-2">
      {/* Top Banner */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-cyan-400 uppercase tracking-widest mb-2">
              <FiSearch className="w-4 h-4 stroke-[2.5]" />
              Digital Forensics Control Center
            </div>
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">
              Investigative Case Portfolio
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Manage digital evidence repositories, multi-format forensic extractions, and AI-grounded intelligence graphs.
            </p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs tracking-wider uppercase shadow-xl shadow-cyan-500/25 transition-all flex items-center justify-center gap-2.5 cursor-pointer shrink-0"
          >
            <FiFolderPlus className="w-5 h-5" />
            Open New Case
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <FiFolder className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">{cases.length}</div>
            <div className="text-xs text-slate-400 font-mono mt-0.5">Active Cases</div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <FiHardDrive className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">8 Supported</div>
            <div className="text-xs text-slate-400 font-mono mt-0.5">Forensic Parsers</div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center text-violet-400">
            <FiActivity className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">pgvector</div>
            <div className="text-xs text-slate-400 font-mono mt-0.5">384-Dim Vector RAG</div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <FiCheckCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-100">SHA-256</div>
            <div className="text-xs text-slate-400 font-mono mt-0.5">Chain of Custody</div>
          </div>
        </div>
      </div>

      {/* Case Grid */}
      <div>
        <h3 className="text-base font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <FiFolder className="text-cyan-400 w-5 h-5" />
          Active Investigations ({cases.length})
        </h3>

        {loading && cases.length === 0 ? (
          <div className="py-16 text-center text-xs font-mono text-slate-400 animate-pulse">
            Loading investigation cases...
          </div>
        ) : cases.length === 0 ? (
          <div className="glass-panel p-12 rounded-2xl border border-dashed border-slate-800 text-center">
            <FiFolder className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <h4 className="text-base font-semibold text-slate-300">No cases initialized</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Create your first forensic case to begin ingesting multi-channel evidence and reconstructing timelines.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="mt-6 px-5 py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 font-semibold text-xs transition-all inline-flex items-center gap-2"
            >
              <FiFolderPlus className="w-4 h-4" />
              Initialize Case
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cases.map((c) => (
              <div
                key={c.id}
                onClick={() => handleSelectCase(c)}
                className="glass-panel glass-panel-hover p-6 rounded-2xl border border-slate-800 cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/40">
                      CASE
                    </span>
                    <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                      <FiClock className="w-3 h-3" />
                      {new Date(c.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h4 className="text-base font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">
                    {c.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                    {c.description || 'No detailed case scope provided.'}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-500 truncate max-w-[150px]">
                    ID: {c.id.slice(0, 10)}...
                  </span>
                  <span className="text-xs font-semibold text-cyan-400 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                    Open Workspace <FiArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Case Creation Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <FiFolderPlus className="text-cyan-400 w-5 h-5" />
            <span>Open New Forensic Case</span>
          </div>
        }
      >
        <form onSubmit={handleCreateCase} className="space-y-4 text-left">
          <div>
            <label className="block text-xs font-mono font-medium text-slate-400 mb-1.5">
              CASE OPERATION TITLE
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Operation Sovereign Vault"
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-2.5 px-3.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-medium text-slate-400 mb-1.5">
              INVESTIGATION SCOPE & OBJECTIVES
            </label>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detail target entities, suspected illegal activities, and operational goals..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-2.5 px-3.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating || !title.trim()}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-cyan-500/25 disabled:opacity-50"
            >
              {creating ? 'Initializing...' : 'Create Case'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
