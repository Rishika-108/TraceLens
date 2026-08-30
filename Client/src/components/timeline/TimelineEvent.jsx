import React from 'react';
import {
  FiPhone,
  FiMessageSquare,
  FiMessageCircle,
  FiMail,
  FiGlobe,
  FiFileText,
  FiImage,
  FiClock,
  FiLayers,
  FiActivity,
  FiRadio,
  FiMapPin,
  FiWifi,
  FiSearch,
  FiAlertTriangle,
} from 'react-icons/fi';

const CHANNEL_CONFIG = {
  PHONE_COMMUNICATION: {
    icon: FiPhone,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/30',
    badge: 'PHONE CALL',
  },
  CALL: {
    icon: FiPhone,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/30',
    badge: 'PHONE CALL',
  },
  CHAT_COMMUNICATION: {
    icon: FiMessageSquare,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    badge: 'WHATSAPP CHAT',
  },
  WHATSAPP_MESSAGE: {
    icon: FiMessageSquare,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    badge: 'WHATSAPP CHAT',
  },
  SMS_COMMUNICATION: {
    icon: FiMessageCircle,
    color: 'text-sky-400',
    bg: 'bg-sky-500/10 border-sky-500/30',
    badge: 'SMS MESSAGE',
  },
  SMS: {
    icon: FiMessageCircle,
    color: 'text-sky-400',
    bg: 'bg-sky-500/10 border-sky-500/30',
    badge: 'SMS MESSAGE',
  },
  EMAIL_COMMUNICATION: {
    icon: FiMail,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/30',
    badge: 'EMAIL RECORD',
  },
  EMAIL: {
    icon: FiMail,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/30',
    badge: 'EMAIL RECORD',
  },
  WEB_NAVIGATION: {
    icon: FiGlobe,
    color: 'text-violet-400',
    bg: 'bg-violet-500/10 border-violet-500/30',
    badge: 'WEB NAVIGATION',
  },
  WEB_SEARCH_QUERY: {
    icon: FiSearch,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    badge: 'SEARCH QUERY',
  },
  BROWSER_HISTORY: {
    icon: FiGlobe,
    color: 'text-violet-400',
    bg: 'bg-violet-500/10 border-violet-500/30',
    badge: 'WEB NAVIGATION',
  },
  DOCUMENT_RECORD: {
    icon: FiFileText,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
    badge: 'DOCUMENT EXCERPT',
  },
  DOCUMENT: {
    icon: FiFileText,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
    badge: 'DOCUMENT EXCERPT',
  },
  IMAGE_RECORD: {
    icon: FiImage,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
    badge: 'IMAGE EXIF',
  },
  IMAGE_CAPTURE: {
    icon: FiImage,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
    badge: 'IMAGE EXIF',
  },
  TELEMETRY_CELL_TOWER: {
    icon: FiRadio,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/30',
    badge: 'CELL TOWER',
  },
  TELEMETRY_GEOLOCATION: {
    icon: FiMapPin,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
    badge: 'GPS TELEMETRY',
  },
  NETWORK_CONNECTION: {
    icon: FiWifi,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/30',
    badge: 'NETWORK FLOW',
  },
  SYSTEM_AUDIT_EVENT: {
    icon: FiAlertTriangle,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
    badge: 'SYSTEM AUDIT',
  },
};

export const TimelineEvent = ({ event, index }) => {
  const config = CHANNEL_CONFIG[event.event_type] || {
    icon: FiActivity,
    color: 'text-slate-400',
    bg: 'bg-slate-500/10 border-slate-500/30',
    badge: event.event_type,
  };
  const Icon = config.icon;

  const eventDate = event.event_timestamp ? new Date(event.event_timestamp) : null;
  const timeFormatted = eventDate
    ? eventDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : 'Unknown Time';
  const dateFormatted = eventDate ? eventDate.toLocaleDateString() : 'Unknown Date';

  const state = event.event_state || (
    event.description?.includes('[PLAN') ? 'PLANNED' :
    event.description?.includes('[ACKNOWLEDGED]') ? 'ACKNOWLEDGED' :
    event.description?.includes('[OCCURRED]') || event.description?.includes('[VERIFIED]') ? 'OCCURRED' :
    'RECORDED'
  );

  const cleanDescription = (event.description || '')
    .replace(/^\[UNANCHORED TIMESTAMP\]\s*/, '')
    .replace(/^\[PLAN(?:NED EVENT)?(?:\s+at[^\]]+)?\]\s*/, '')
    .replace(/^\[ACKNOWLEDGED\]\s*/, '')
    .replace(/^\[OCCURRED\]\s*/, '')
    .replace(/^\[VERIFIED(?: TELEMETRY)?\]\s*/, '')
    .replace(/^\[RECORDED\]\s*/, '')
    .replace(/^\[MEDIA RECORD\]\s*/, '');

  return (
    <div className="relative pl-8 pb-8 group text-left last:pb-2">
      {/* Vertical Connecting Line */}
      <div className="absolute left-3.5 top-3.5 bottom-0 w-0.5 bg-slate-800 group-last:hidden" />

      {/* Node Dot / Channel Icon */}
      <div
        className={`absolute left-0 top-1 w-7 h-7 rounded-xl border flex items-center justify-center ${config.bg} shadow-sm z-10 transition-transform group-hover:scale-110`}
      >
        <Icon className={`w-3.5 h-3.5 ${config.color}`} />
      </div>

      {/* Event Card Content */}
      <div className="glass-panel glass-panel-hover p-4 rounded-2xl border border-slate-800/80 shadow-md space-y-2.5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${config.bg} ${config.color}`}
            >
              {config.badge}
            </span>

            {/* Event Modality State Badges */}
            {state === 'PLANNED' && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-purple-500/10 border-purple-500/30 text-purple-300">
                PROPOSED / UNVERIFIED
              </span>
            )}
            {state === 'ACKNOWLEDGED' && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-sky-500/10 border-sky-500/30 text-sky-300">
                ACKNOWLEDGED
              </span>
            )}
            {state === 'OCCURRED' && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-emerald-500/10 border-emerald-500/30 text-emerald-300">
                VERIFIED OCCURRENCE
              </span>
            )}
            {state === 'DENIED_OR_CANCELLED' && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-rose-500/10 border-rose-500/30 text-rose-300">
                CANCELLED / DENIED
              </span>
            )}

            {/* Synthetic Timestamp Warning Badge */}
            {event.is_synthetic_timestamp && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-amber-500/10 border-amber-500/30 text-amber-400">
                UNANCHORED TIMESTAMP
              </span>
            )}

            <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
              <FiClock className="w-3 h-3 text-slate-500" />
              {dateFormatted} • {timeFormatted}
            </span>
          </div>

          {event.artifact_id && (
            <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
              <FiLayers className="w-3 h-3 text-slate-600" />
              Art #{event.artifact_id.slice(0, 8)}
            </span>
          )}
        </div>

        {/* Dynamic Actor -> Target Row */}
        {(event.actor || event.target) && (
          <div className="text-[11px] font-mono text-slate-400 flex items-center gap-2">
            <span className="text-slate-300 font-semibold">{event.actor || 'Unknown Source'}</span>
            <span className="text-slate-600">→</span>
            <span className="text-cyan-400">{event.target || 'Unknown Endpoint'}</span>
          </div>
        )}

        {/* Referenced Time & Location Chips */}
        {(event.referenced_time || event.referenced_location) && (
          <div className="flex flex-wrap gap-1.5 pt-0.5">
            {event.referenced_time && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-300 text-[10px] font-mono">
                <FiClock className="w-2.5 h-2.5" /> Proposed Time: {event.referenced_time}
              </span>
            )}
            {event.referenced_location && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[10px] font-mono">
                <FiMapPin className="w-2.5 h-2.5" /> Vicinity: {event.referenced_location}
              </span>
            )}
          </div>
        )}

        <p className="text-xs text-slate-200 leading-relaxed font-normal pt-1">
          {cleanDescription}
        </p>
      </div>
    </div>
  );
};
