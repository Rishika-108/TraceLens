import React, { useState } from 'react';
import {
  FiCpu,
  FiZap,
  FiHelpCircle,
  FiArrowRight,
  FiShield,
  FiCheckCircle,
  FiAlertTriangle,
  FiLayers,
  FiBookmark,
  FiActivity,
} from 'react-icons/fi';
import { useCase } from '../context/CaseContext';
import { searchService } from '../services/search';
import { SemanticSearch } from '../components/search/SemanticSearch';

const SAMPLE_QUESTIONS = [
  'Who requested the money transfer and to which bank account?',
  'What phone numbers and email addresses communicated regarding the payout?',
  'When and where was the physical meeting arranged to take place?',
  'Did any suspect access external browser links or cryptocurrency wallets?',
];

export const Investigation = () => {
  const { activeCase } = useCase();
  const [activeTab, setActiveTab] = useState('agent'); // 'agent' or 'search'
  const [question, setQuestion] = useState('');
  const [investigationResult, setInvestigationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!activeCase) {
    return (
      <div className="py-24 text-center max-w-md mx-auto">
        <FiCpu className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-slate-200">No Target Case Selected</h3>
        <p className="text-xs text-slate-500 mt-1">
          Please select an active investigation case to engage the AI Investigation Agent.
        </p>
      </div>
    );
  }

  const handleInvestigate = async (queryText = question) => {
    const q = queryText.trim();
    if (!q || !activeCase) return;

    setLoading(true);
    setError(null);
    try {
      const data = await searchService.investigateCase(activeCase.id, q);
      setInvestigationResult(data);
    } catch (err) {
      console.error('Investigation failed', err);
      setError(err.response?.data?.detail || 'Investigation agent reasoning failed.');
    } finally {
      setLoading(false);
    }
  };

  // Helper to format Markdown and highlight [FACT] and [INFERENCE] tags
  const renderFormattedAnswer = (text) => {
    if (!text) return null;

    return text.split('\n').map((line, idx) => {
      if (line.startsWith('### ')) {
        return (
          <h4 key={idx} className="text-sm font-bold text-cyan-300 mt-4 mb-2 flex items-center gap-1.5 font-mono">
            <FiBookmark className="w-3.5 h-3.5" />
            {line.replace('### ', '')}
          </h4>
        );
      }

      if (line.startsWith('- [FACT]')) {
        return (
          <div key={idx} className="my-1.5 p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-slate-100 flex items-start gap-2">
            <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono font-bold text-[10px] shrink-0">
              FACT
            </span>
            <span className="leading-relaxed">{line.replace('- [FACT]', '').trim()}</span>
          </div>
        );
      }

      if (line.startsWith('- [INFERENCE]')) {
        return (
          <div key={idx} className="my-1.5 p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-slate-100 flex items-start gap-2">
            <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-mono font-bold text-[10px] shrink-0">
              INFERENCE
            </span>
            <span className="leading-relaxed">{line.replace('- [INFERENCE]', '').trim()}</span>
          </div>
        );
      }

      if (line.startsWith('- [Artifact') || line.startsWith('- [EVIDENCE_REF')) {
        return (
          <div key={idx} className="my-1 text-xs font-mono text-cyan-400 pl-4 border-l border-cyan-500/40">
            {line}
          </div>
        );
      }

      if (!line.trim()) return <div key={idx} className="h-1.5" />;

      return (
        <p key={idx} className="text-xs text-slate-300 leading-relaxed my-1">
          {line}
        </p>
      );
    });
  };

  return (
    <div className="space-y-6 text-left max-w-7xl mx-auto p-2">
      {/* Top Banner & Mode Switcher */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-violet-400 uppercase tracking-widest mb-1.5">
            <FiCpu className="w-4 h-4" />
            <span>AI Reasoning & Retrieval Hub</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Case Investigation Agent
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            RAG-powered conversational forensics with evidentiary grounding, citation integrity, and strict fact/inference separation.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex rounded-2xl bg-slate-900 border border-slate-800 p-1 shrink-0">
          <button
            onClick={() => setActiveTab('agent')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === 'agent'
                ? 'bg-gradient-to-r from-violet-500/20 to-indigo-500/20 text-violet-300 border border-violet-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FiCpu className="w-4 h-4 text-violet-400" />
            Investigation Agent
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === 'search'
                ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FiZap className="w-4 h-4 text-cyan-400" />
            Semantic Search
          </button>
        </div>
      </div>

      {activeTab === 'search' ? (
        <SemanticSearch caseId={activeCase.id} />
      ) : (
        <div className="space-y-6">
          {/* Question Input Card */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div>
              <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <FiHelpCircle className="text-violet-400 w-5 h-5" />
                Investigative Inquiry
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Formulate questions regarding suspects, communications, amounts, or temporal correlations.
              </p>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleInvestigate();
              }}
              className="space-y-3"
            >
              <div className="relative">
                <textarea
                  rows={3}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g. Who requested the payment, what account details were provided, and what communications followed?..."
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500 transition-colors shadow-inner"
                />
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                {/* Sample Prompt Chips */}
                <div className="flex flex-wrap gap-1.5">
                  {SAMPLE_QUESTIONS.map((sample, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setQuestion(sample);
                        handleInvestigate(sample);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-slate-900/60 hover:bg-slate-900 border border-slate-800 text-[11px] text-slate-400 hover:text-violet-300 transition-all text-left"
                    >
                      {sample}
                    </button>
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={loading || !question.trim()}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-violet-500 via-indigo-500 to-cyan-500 hover:from-violet-400 hover:to-cyan-400 text-slate-950 font-bold text-xs tracking-wider uppercase shadow-xl shadow-violet-500/25 transition-all flex items-center justify-center gap-2 shrink-0 cursor-pointer disabled:opacity-50"
                >
                  <FiCpu className="w-4 h-4" />
                  <span>{loading ? 'Synthesizing...' : 'Run Investigation'}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Loading Animation */}
          {loading && (
            <div className="glass-panel p-16 rounded-2xl border border-slate-800 text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center text-violet-400 mx-auto animate-spin">
                <FiCpu className="w-6 h-6" />
              </div>
              <div className="text-sm font-semibold text-slate-200">
                Retrieving Grounded Case Context & Synthesizing Findings...
              </div>
              <div className="text-xs font-mono text-slate-500">
                Enforcing forensic rules: No hallucination • Mandatory citations • Fact vs Inference
              </div>
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
              <FiAlertTriangle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Investigation Response Card */}
          {investigationResult && !loading && (
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-6">
              {/* Answer Metrics Header */}
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-600 flex items-center justify-center text-white shadow-lg shadow-violet-500/20">
                    <FiShield className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-100">
                      Grounded Investigative Intelligence Assessment
                    </h3>
                    <div className="text-xs text-slate-400">
                      Query: "{investigationResult.question}"
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {/* Confidence Score Pill */}
                  <div className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Confidence:</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {Math.round((investigationResult.confidence || 0) * 100)}%
                    </span>
                  </div>

                  <div className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Citations:</span>
                    <span className="text-xs font-mono font-bold text-cyan-400">
                      {investigationResult.citations_count || investigationResult.evidence_references?.length || 0} Artifacts
                    </span>
                  </div>
                </div>
              </div>

              {/* Formatted Answer Body */}
              <div className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800/80 leading-relaxed">
                {renderFormattedAnswer(investigationResult.answer)}
              </div>

              {/* Supporting Evidence References List */}
              {investigationResult.evidence_references && investigationResult.evidence_references.length > 0 && (
                <div>
                  <div className="text-xs font-mono text-slate-400 mb-3 flex items-center gap-2">
                    <FiLayers className="text-cyan-400" />
                    SUPPORTING SOURCE ARTIFACTS ({investigationResult.evidence_references.length})
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {investigationResult.evidence_references.map((art, idx) => (
                      <div
                        key={art.artifact_id || idx}
                        className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono"
                      >
                        <div className="flex items-center justify-between text-cyan-400 mb-1">
                          <span>Art #{art.artifact_id?.slice(0, 8) || `ART-${idx + 1}`}</span>
                          <span className="text-[10px] text-slate-500">{art.artifact_type}</span>
                        </div>
                        <div className="text-[11px] text-slate-300 truncate">
                          {art.content ? Object.values(art.content)[0] : 'Evidence Item'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
