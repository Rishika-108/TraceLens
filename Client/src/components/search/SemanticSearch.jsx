import React, { useState } from 'react';
import {
  FiSearch,
  FiZap,
  FiSliders,
  FiArrowRight,
  FiCheckCircle,
} from 'react-icons/fi';
import { SearchResults } from './SearchResults';
import { searchService } from '../../services/search';

const SUGGESTED_QUERIES = [
  'Money transfer and bank accounts',
  'Meet locations and timeline arrangements',
  'Bitcoin and crypto wallet payout addresses',
  'Phone calls and communications after midnight',
  'Confidential offshore wire receipts',
];

export const SemanticSearch = ({ caseId }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [limit, setLimit] = useState(10);

  const handleSearch = async (searchStr = query) => {
    const q = searchStr.trim();
    if (!q || !caseId) return;

    setLoading(true);
    setHasSearched(true);
    try {
      const data = await searchService.semanticSearch(caseId, q, limit);
      setResults(data.results || []);
    } catch (err) {
      console.error('Semantic search failed', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleChipClick = (suggestion) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  return (
    <div className="space-y-6 text-left">
      {/* Search Header Box */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <FiZap className="text-cyan-400 w-5 h-5" />
            pgvector Semantic Evidence Search
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Query across multi-format digital evidence using natural language similarity in 384-dimensional vector space.
          </p>
        </div>

        {/* Search Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row gap-2"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask or search: e.g. 'Who mentioned the offshore wire transfer to Zurich?'..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 shadow-inner transition-colors"
            />
            <FiSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs tracking-wider uppercase shadow-lg shadow-cyan-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            <span>{loading ? 'Searching...' : 'Vector Search'}</span>
            <FiArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Suggested Query Chips */}
        <div>
          <div className="text-[10px] font-mono text-slate-500 uppercase mb-2">
            INVESTIGATIVE QUERY TEMPLATES
          </div>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_QUERIES.map((suggestion, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleChipClick(suggestion)}
                className="px-2.5 py-1 rounded-lg bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 text-[11px] text-slate-400 hover:text-cyan-300 transition-all text-left"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search Results Box */}
      {loading ? (
        <div className="glass-panel p-16 rounded-2xl border border-slate-800 text-center text-xs font-mono text-cyan-400 animate-pulse">
          Computing cosine vector similarity across case artifacts...
        </div>
      ) : hasSearched ? (
        <SearchResults results={results} query={query} />
      ) : null}
    </div>
  );
};
