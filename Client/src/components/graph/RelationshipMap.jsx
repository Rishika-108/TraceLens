import React, { useState, useEffect, useMemo } from 'react';
import {
  FiShare2,
  FiSliders,
  FiRefreshCw,
  FiLayers,
  FiUsers,
  FiList,
  FiGrid,
  FiSearch,
  FiArrowRight,
  FiCopy,
  FiCheck,
  FiFilter,
} from 'react-icons/fi';
import { GraphView } from './GraphView';
import { intelligenceService } from '../../services/intelligence';

const TYPE_COLORS = {
  PERSON: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
  PHONE: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  EMAIL: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30',
  CRYPTO_ADDRESS: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  IP_ADDRESS: 'bg-violet-500/10 text-violet-300 border-violet-500/30',
  ORG: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
  LOCATION: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
  DOMAIN: 'bg-teal-500/10 text-teal-300 border-teal-500/30',
};

export const RelationshipMap = ({ caseId }) => {
  const [entities, setEntities] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(false);
  const [minConfidence, setMinConfidence] = useState(0.5);
  const [viewMode, setViewMode] = useState('graph'); // 'graph' or 'endpoints'
  const [matrixSearch, setMatrixSearch] = useState('');
  const [copiedId, setCopiedId] = useState(null);

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

  // Build entity map for fast endpoint lookup
  const entityMap = useMemo(() => {
    const map = new Map();
    entities.forEach((e) => map.set(e.id, e));
    return map;
  }, [entities]);

  // Enrich relationships with resolved endpoints
  const resolvedRelationships = useMemo(() => {
    return relationships.map((rel) => {
      const src = entityMap.get(rel.source_entity_id);
      const tgt = entityMap.get(rel.target_entity_id);
      return {
        ...rel,
        source_val: rel.source_entity_value || src?.value || 'Unknown Source',
        source_typ: rel.source_entity_type || src?.entity_type || 'ENTITY',
        target_val: rel.target_entity_value || tgt?.value || 'Unknown Target',
        target_typ: rel.target_entity_type || tgt?.entity_type || 'ENTITY',
      };
    });
  }, [relationships, entityMap]);

  // Filtered relationships for the endpoints matrix
  const filteredMatrixRelationships = useMemo(() => {
    return resolvedRelationships.filter((r) => {
      const conf = parseFloat(r.confidence || 0);
      const matchesConf = conf >= minConfidence;
      const q = matrixSearch.trim().toLowerCase();
      const matchesQuery =
        !q ||
        r.source_val.toLowerCase().includes(q) ||
        r.target_val.toLowerCase().includes(q) ||
        r.relationship_type.toLowerCase().includes(q) ||
        r.source_typ.toLowerCase().includes(q) ||
        r.target_typ.toLowerCase().includes(q);
      return matchesConf && matchesQuery;
    });
  }, [resolvedRelationships, minConfidence, matrixSearch]);

  const copyValue = (val, key) => {
    navigator.clipboard.writeText(val);
    setCopiedId(key);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-6 text-left">
      {/* Controls & Metrics Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
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
            {/* View Mode Switcher */}
            <div className="flex rounded-xl bg-slate-900 border border-slate-800 p-0.5">
              <button
                onClick={() => setViewMode('graph')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  viewMode === 'graph' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Graph Network View"
              >
                <FiShare2 className="w-3.5 h-3.5" />
                Network Graph
              </button>
              <button
                onClick={() => setViewMode('endpoints')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  viewMode === 'endpoints' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Relationship Endpoints Matrix"
              >
                <FiList className="w-3.5 h-3.5" />
                Endpoints Matrix ({resolvedRelationships.length})
              </button>
            </div>

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

        {/* Filters Row */}
        <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
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

          {viewMode === 'endpoints' && (
            <div className="relative w-full sm:w-72">
              <input
                type="text"
                value={matrixSearch}
                onChange={(e) => setMatrixSearch(e.target.value)}
                placeholder="Filter endpoints by name, number, type..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-1.5 pl-8 pr-3 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <FiSearch className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500 w-3.5 h-3.5" />
            </div>
          )}
        </div>
      </div>

      {/* Main Content: Graph or Endpoints Matrix */}
      {loading && entities.length === 0 ? (
        <div className="glass-panel p-24 rounded-2xl border border-slate-800 text-center text-xs font-mono text-slate-400 animate-pulse">
          Computing communication network topology & relationship endpoints...
        </div>
      ) : entities.length === 0 ? (
        <div className="glass-panel p-24 rounded-2xl border border-dashed border-slate-800 text-center">
          <FiShare2 className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h4 className="text-base font-semibold text-slate-300">No relationships mapped yet</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Ingest multi-party evidence files to discover communications and co-occurrence graphs.
          </p>
        </div>
      ) : viewMode === 'graph' ? (
        <GraphView
          entities={entities}
          relationships={relationships}
          minConfidence={minConfidence}
        />
      ) : (
        /* Relationship Endpoints Matrix Table */
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <FiLayers className="text-cyan-400" />
              Verified Relationship Endpoints ({filteredMatrixRelationships.length})
            </h4>
            <span className="text-[11px] font-mono text-slate-500">
              Filtered at ≥{(minConfidence * 100).toFixed(0)}% confidence
            </span>
          </div>

          {filteredMatrixRelationships.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 font-mono">
              No relationship endpoints match current filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    <th className="py-3 px-3">Source Endpoint</th>
                    <th className="py-3 px-3 text-center">Relationship Channel</th>
                    <th className="py-3 px-3">Target Endpoint</th>
                    <th className="py-3 px-3">Supporting Evidence</th>
                    <th className="py-3 px-3 text-right">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
                  {filteredMatrixRelationships.map((rel, idx) => {
                    const conf = parseFloat(rel.confidence || 0);
                    const srcStyle = TYPE_COLORS[rel.source_typ] || 'bg-slate-900 text-slate-300 border-slate-800';
                    const tgtStyle = TYPE_COLORS[rel.target_typ] || 'bg-slate-900 text-slate-300 border-slate-800';

                    return (
                      <tr key={rel.id || idx} className="hover:bg-slate-900/40 transition-colors">
                        {/* Source Endpoint */}
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase shrink-0 ${srcStyle}`}>
                              {rel.source_typ}
                            </span>
                            <span className="text-slate-100 font-semibold truncate max-w-[180px]" title={rel.source_val}>
                              {rel.source_val}
                            </span>
                          </div>
                        </td>

                        {/* Relationship Link */}
                        <td className="py-3 px-3 text-center">
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 text-[11px]">
                            <span className="font-bold text-cyan-400">{rel.relationship_type}</span>
                            <FiArrowRight className="text-slate-500 w-3 h-3" />
                          </div>
                        </td>

                        {/* Target Endpoint */}
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase shrink-0 ${tgtStyle}`}>
                              {rel.target_typ}
                            </span>
                            <span className="text-slate-100 font-semibold truncate max-w-[180px]" title={rel.target_val}>
                              {rel.target_val}
                            </span>
                          </div>
                        </td>

                        {/* Supporting Evidence */}
                        <td className="py-3 px-3 text-slate-400 text-[11px] max-w-[240px]">
                          {rel.evidence_snippet ? (
                            <div className="truncate" title={rel.evidence_snippet}>
                              {rel.supporting_artifact_id && (
                                <span className="text-[10px] text-cyan-400 mr-1.5 font-mono">
                                  [#{rel.supporting_artifact_id.slice(0, 8)}]
                                </span>
                              )}
                              <span>{rel.evidence_snippet}</span>
                            </div>
                          ) : (
                            <span className="text-slate-600 text-[10px]">Corroborated in evidence</span>
                          )}
                        </td>

                        {/* Confidence Score */}
                        <td className="py-3 px-3 text-right">
                          <span
                            className={`px-2 py-0.5 rounded-lg border font-mono font-bold text-[11px] ${
                              conf >= 0.85
                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                                : 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300'
                            }`}
                          >
                            {(conf * 100).toFixed(0)}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
