import React, { useState, useEffect } from 'react';
import {
  FiUsers,
  FiSearch,
  FiCopy,
  FiCheck,
  FiRefreshCw,
  FiGrid,
  FiList,
  FiUser,
  FiPhone,
  FiMail,
  FiKey,
  FiGlobe,
  FiMapPin,
  FiBriefcase,
} from 'react-icons/fi';
import { EntityCard } from './EntityCard';
import { intelligenceService } from '../../services/intelligence';

const TYPE_TABS = [
  { id: 'ALL', label: 'All Entities' },
  { id: 'PERSON', label: 'People / Suspects', icon: FiUser },
  { id: 'PHONE', label: 'Phone Numbers', icon: FiPhone },
  { id: 'EMAIL', label: 'Email Addresses', icon: FiMail },
  { id: 'CRYPTO_ADDRESS', label: 'Crypto Wallets', icon: FiKey },
  { id: 'IP_ADDRESS', label: 'IP Addresses', icon: FiGlobe },
  { id: 'ORG', label: 'Organizations', icon: FiBriefcase },
  { id: 'LOCATION', label: 'Locations', icon: FiMapPin },
];

export const EntityTable = ({ caseId }) => {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [copiedValue, setCopiedValue] = useState(null);

  const fetchEntities = async () => {
    if (!caseId) return;
    setLoading(true);
    try {
      const data = await intelligenceService.getEntitiesByCase(caseId);
      setEntities(data);
    } catch (err) {
      console.error('Failed to fetch entities', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntities();
  }, [caseId]);

  const copyToClipboard = (val) => {
    navigator.clipboard.writeText(val);
    setCopiedValue(val);
    setTimeout(() => setCopiedValue(null), 2000);
  };

  const filteredEntities = entities.filter((ent) => {
    const matchesType = selectedType === 'ALL' || ent.entity_type === selectedType;
    const matchesSearch =
      !searchQuery.trim() ||
      ent.value?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ent.entity_type?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-6 text-left">
      {/* Controls Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <FiUsers className="text-cyan-400 w-5 h-5" />
              Extracted Forensic Entities ({filteredEntities.length})
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Structured directory of discovered suspect names, phones, email addresses, crypto wallets, and locations.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex rounded-xl bg-slate-900 border border-slate-800 p-0.5">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg transition-colors ${
                  viewMode === 'grid' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Grid View"
              >
                <FiGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-lg transition-colors ${
                  viewMode === 'table' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Table View"
              >
                <FiList className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={fetchEntities}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-colors"
              title="Refresh Entities"
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Filter Tabs & Search */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by entity name, phone, BTC wallet, IP address..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-2 pl-9 pr-4 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
            />
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-3.5 h-3.5" />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {TYPE_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedType(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium border whitespace-nowrap transition-all ${
                  selectedType === tab.id
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm shadow-cyan-500/10'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Entities Content (Grid or Table) */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        {loading && entities.length === 0 ? (
          <div className="py-16 text-center text-xs font-mono text-slate-400 animate-pulse">
            Extracting entities from case evidence artifacts...
          </div>
        ) : filteredEntities.length === 0 ? (
          <div className="py-16 text-center border border-dashed border-slate-800 rounded-xl">
            <FiUsers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <div className="text-sm font-semibold text-slate-400">No matching entities found</div>
            <div className="text-xs text-slate-500 mt-1">
              Upload case evidence files to extract multi-type forensic entities.
            </div>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {filteredEntities.map((ent) => (
              <EntityCard
                key={ent.id}
                entity={ent}
                onCopy={copyToClipboard}
                isCopied={copiedValue === ent.value}
              />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-3">Entity Type</th>
                  <th className="py-3 px-3">Discovered Value</th>
                  <th className="py-3 px-3">Linked Artifact</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-xs font-mono">
                {filteredEntities.map((ent) => (
                  <tr key={ent.id} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-[10px] text-cyan-400 font-bold">
                        {ent.entity_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-200 font-semibold break-all">
                      {ent.value}
                    </td>
                    <td className="py-3 px-3 text-slate-500 text-[10px]">
                      {ent.artifact_id ? `Art #${ent.artifact_id.slice(0, 8)}` : 'N/A'}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => copyToClipboard(ent.value)}
                        className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition-colors inline-flex items-center gap-1 text-[11px]"
                      >
                        {copiedValue === ent.value ? (
                          <>
                            <FiCheck className="w-3.5 h-3.5 text-emerald-400" /> Copied
                          </>
                        ) : (
                          <>
                            <FiCopy className="w-3.5 h-3.5" /> Copy
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
