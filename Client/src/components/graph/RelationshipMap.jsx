import React, { useState, useEffect } from 'react';
import {
  FiShare2,
  FiSliders,
  FiRefreshCw,
  FiLayers,
  FiUsers,
} from 'react-icons/fi';
import { GraphView } from './GraphView';
import { intelligenceService } from '../../services/intelligence';

export const RelationshipMap = ({ caseId }) => {
  const [entities, setEntities] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(false);
  const [minConfidence, setMinConfidence] = useState(0.5);

  const fetchGraphData = async () => {
    if (!caseId) return;
    setLoading(true);
    try {
      const [ents, rels] = await Promise.all([
        intelligenceService.getEntitiesByCase(caseId),
        intelligenceService.getRelationshipsByCase(caseId),
      ]);
      setEntities(ents);
      setRelationships(rels);
    } catch (err) {
      console.error('Failed to load relationship graph data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, [caseId]);

  return (
    <div className="space-y-6 text-left">
      {/* Controls & Metrics Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <FiShare2 className="text-indigo-400 w-5 h-5" />
              Suspect Communication & Relationship Network
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Interactive topology mapping direct communications (Calls, SMS, WhatsApp, Email) and artifact co-occurrences.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Metrics Pills */}
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-cyan-400">
                {entities.length} Nodes
              </span>
              <span className="px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-indigo-400">
                {relationships.length} Links
              </span>
            </div>

            <button
              onClick={fetchGraphData}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-colors"
              title="Refresh Graph"
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Confidence Filter Slider */}
        <div className="mt-4 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full sm:w-80">
            <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5 shrink-0">
              <FiSliders className="text-cyan-400 w-3.5 h-3.5" />
              Min Confidence:
            </span>
            <input
              type="range"
              min="0.5"
              max="0.95"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <span className="text-xs font-mono font-bold text-cyan-400 shrink-0">
              {(minConfidence * 100).toFixed(0)}%
            </span>
          </div>

          <div className="text-[11px] font-mono text-slate-500">
            Click any entity node to inspect metadata and connected channels
          </div>
        </div>
      </div>

      {/* ReactFlow Graph Canvas */}
      {loading && entities.length === 0 ? (
        <div className="glass-panel p-24 rounded-2xl border border-slate-800 text-center text-xs font-mono text-slate-400 animate-pulse">
          Computing communication network topology...
        </div>
      ) : entities.length === 0 ? (
        <div className="glass-panel p-24 rounded-2xl border border-dashed border-slate-800 text-center">
          <FiShare2 className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h4 className="text-base font-semibold text-slate-300">No relationships mapped yet</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Ingest multi-party evidence files to discover communications and co-occurrence graphs.
          </p>
        </div>
      ) : (
        <GraphView
          entities={entities}
          relationships={relationships}
          minConfidence={minConfidence}
        />
      )}
    </div>
  );
};
