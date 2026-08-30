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
  IMAGE_CAPTURE: {
    icon: FiImage,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
    badge: 'IMAGE EXIF',
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

  const isPlanned = event.description?.includes('[PLAN / PROPOSED]');
  const isVerified = event.description?.includes('[VERIFIED]');
  const cleanDescription = (event.description || '')
    .replace(/^\[PLAN \/ PROPOSED\]\s*/, '')
    .replace(/^\[VERIFIED\]\s*/, '')
    .replace(/^\[RECORDED\]\s*/, '');

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
      <div className="glass-panel glass-panel-hover p-4 rounded-2xl border border-slate-800/80 shadow-md">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2">
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${config.bg} ${config.color}`}
            >
              {config.badge}
            </span>

            {isPlanned && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-amber-500/10 border-amber-500/30 text-amber-300">
                PROPOSED / UNVERIFIED
              </span>
            )}

            {isVerified && (
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full border bg-emerald-500/10 border-emerald-500/30 text-emerald-300">
                VERIFIED OCCURRENCE
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

        <p className="text-xs text-slate-200 leading-relaxed font-normal">
          {cleanDescription}
        </p>
      </div>
    </div>
  );
};
