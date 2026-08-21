import React, { useState, useEffect } from 'react';
import {
  FiClock,
  FiSearch,
  FiFilter,
  FiArrowUp,
  FiArrowDown,
  FiRefreshCw,
  FiPhone,
  FiMessageSquare,
  FiMail,
  FiGlobe,
  FiFileText,
} from 'react-icons/fi';
import { TimelineEvent } from './TimelineEvent';
import { intelligenceService } from '../../services/intelligence';

const CHANNEL_FILTERS = [
  { id: 'ALL', label: 'All Channels' },
  { id: 'PHONE_COMMUNICATION', label: 'Phone Calls', icon: FiPhone },
  { id: 'CHAT_COMMUNICATION', label: 'WhatsApp', icon: FiMessageSquare },
  { id: 'SMS_COMMUNICATION', label: 'SMS', icon: FiMessageSquare },
  { id: 'EMAIL_COMMUNICATION', label: 'Emails', icon: FiMail },
  { id: 'WEB_NAVIGATION', label: 'Web Browsing', icon: FiGlobe },
  { id: 'DOCUMENT_RECORD', label: 'Documents', icon: FiFileText },
];

export const Timeline = ({ caseId }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortAsc, setSortAsc] = useState(true);

  const fetchTimeline = async () => {
    if (!caseId) return;
    setLoading(true);
    try {
      const data = await intelligenceService.getTimelineByCase(caseId);
      setEvents(data);
    } catch (err) {
      console.error('Failed to fetch timeline events', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, [caseId]);

  // Filter events
  const filteredEvents = events.filter((ev) => {
    const matchesChannel =
      selectedChannel === 'ALL' ||
      ev.event_type === selectedChannel ||
      (selectedChannel === 'PHONE_COMMUNICATION' && ev.event_type === 'CALL') ||
      (selectedChannel === 'CHAT_COMMUNICATION' && ev.event_type === 'WHATSAPP_MESSAGE') ||
      (selectedChannel === 'SMS_COMMUNICATION' && ev.event_type === 'SMS') ||
      (selectedChannel === 'EMAIL_COMMUNICATION' && ev.event_type === 'EMAIL') ||
      (selectedChannel === 'WEB_NAVIGATION' && ev.event_type === 'BROWSER_HISTORY') ||
      (selectedChannel === 'DOCUMENT_RECORD' && ev.event_type === 'DOCUMENT');

    const matchesSearch =
      !searchQuery.trim() ||
      ev.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.event_type?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesChannel && matchesSearch;
  });

  // Sort events
  const sortedEvents = [...filteredEvents].sort((a, b) => {
    const tA = new Date(a.event_timestamp || 0).getTime();
    const tB = new Date(b.event_timestamp || 0).getTime();
    return sortAsc ? tA - tB : tB - tA;
  });

  return (
    <div className="space-y-6 text-left">
      {/* Controls Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
              <FiClock className="text-cyan-400 w-5 h-5" />
              Reconstructed Incident Timeline ({sortedEvents.length} Events)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Normalized chronological sequence across phone calls, chat transcripts, emails, and web records.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setSortAsc(!sortAsc)}
              className="px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-mono flex items-center gap-1.5 transition-colors"
            >
              {sortAsc ? (
                <>
                  <FiArrowUp className="text-cyan-400" /> Oldest First
                </>
              ) : (
                <>
                  <FiArrowDown className="text-cyan-400" /> Newest First
                </>
              )}
            </button>

            <button
              onClick={fetchTimeline}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-cyan-400 transition-colors"
              title="Refresh Timeline"
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter timeline by suspect, phone number, keyword..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl py-2 pl-9 pr-4 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
            />
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-3.5 h-3.5" />
          </div>

          {/* Channel Filters */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {CHANNEL_FILTERS.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedChannel(cat.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium border whitespace-nowrap transition-all ${
                  selectedChannel === cat.id
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm shadow-cyan-500/10'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        {loading && events.length === 0 ? (
          <div className="py-16 text-center text-xs font-mono text-slate-400 animate-pulse">
            Reconstructing case timeline events...
          </div>
        ) : sortedEvents.length === 0 ? (
          <div className="py-16 text-center border border-dashed border-slate-800 rounded-xl">
            <FiClock className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <div className="text-sm font-semibold text-slate-400">No matching timeline events found</div>
            <div className="text-xs text-slate-500 mt-1">
              Ingest evidence with timestamps to generate chronological events.
            </div>
          </div>
        ) : (
          <div className="relative pt-2">
            {sortedEvents.map((ev, index) => (
              <TimelineEvent key={ev.id || index} event={ev} index={index} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
