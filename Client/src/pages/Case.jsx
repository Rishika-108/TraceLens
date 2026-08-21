import React, { useState } from 'react';
import {
  FiHardDrive,
  FiClock,
  FiShare2,
  FiUsers,
  FiChevronRight,
} from 'react-icons/fi';
import { useCase } from '../context/CaseContext';
import { EvidenceUpload } from '../components/evidence/EvidenceUpload';
import { EvidenceList } from '../components/evidence/EvidenceList';
import { Timeline } from '../components/timeline/Timeline';
import { RelationshipMap } from '../components/graph/RelationshipMap';
import { EntityTable } from '../components/entities/EntityTable';

export const Case = () => {
  const { activeCase } = useCase();
  const [activeTab, setActiveTab] = useState('evidence');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  if (!activeCase) {
    return (
      <div className="py-24 text-center max-w-md mx-auto">
        <FiHardDrive className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-slate-200">No Target Case Selected</h3>
        <p className="text-xs text-slate-500 mt-1">
          Please select an active case from the top navigation dropdown or portfolio dashboard.
        </p>
      </div>
    );
  }

  const tabs = [
    { id: 'evidence', label: 'Evidence & Ingestion', icon: FiHardDrive },
    { id: 'timeline', label: 'Timeline Reconstructed', icon: FiClock },
    { id: 'graph', label: 'Relationship Graph', icon: FiShare2 },
    { id: 'entities', label: 'Forensic Entities', icon: FiUsers },
  ];

  return (
    <div className="space-y-6 text-left max-w-7xl mx-auto p-2">
      {/* Case Header Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest mb-1.5">
              <span>Operation Workspace</span>
              <FiChevronRight className="w-3 h-3 text-slate-600" />
              <span className="text-slate-400">{activeCase.id}</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              {activeCase.title}
            </h1>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
              {activeCase.description || 'Target case for multi-format evidence ingestion, timeline reconstruction, and intelligence graphing.'}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Active Workspace
            </span>
          </div>
        </div>

        {/* Workspace Tab Bar */}
        <div className="flex items-center gap-2 mt-6 pt-4 border-t border-slate-800/80 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold border transition-all shrink-0 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/15 to-indigo-500/10 text-cyan-300 border-cyan-500/40 shadow-sm shadow-cyan-500/10'
                    : 'bg-slate-900/40 border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Contents */}
      {activeTab === 'evidence' && (
        <div className="space-y-6">
          <EvidenceUpload
            caseId={activeCase.id}
            onUploadSuccess={() => setRefreshTrigger((prev) => prev + 1)}
          />
          <EvidenceList caseId={activeCase.id} refreshTrigger={refreshTrigger} />
        </div>
      )}

      {activeTab === 'timeline' && (
        <Timeline caseId={activeCase.id} />
      )}

      {activeTab === 'graph' && (
        <RelationshipMap caseId={activeCase.id} />
      )}

      {activeTab === 'entities' && (
        <EntityTable caseId={activeCase.id} />
      )}
    </div>
  );
};
