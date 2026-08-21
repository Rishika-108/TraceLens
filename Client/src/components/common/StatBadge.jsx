import React from 'react';

const STATUS_CONFIGS = {
  COMPLETED: {
    label: 'Completed',
    bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    dot: 'bg-emerald-400',
  },
  PROCESSING: {
    label: 'Processing',
    bg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 animate-pulse',
    dot: 'bg-cyan-400 animate-ping',
  },
  PARSED: {
    label: 'Parsed',
    bg: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    dot: 'bg-blue-400',
  },
  NORMALIZED: {
    label: 'Normalized',
    bg: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400',
    dot: 'bg-indigo-400',
  },
  INDEXED: {
    label: 'Indexed',
    bg: 'bg-violet-500/10 border-violet-500/30 text-violet-400',
    dot: 'bg-violet-400',
  },
  FAILED: {
    label: 'Failed',
    bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
    dot: 'bg-rose-400',
  },
  PENDING: {
    label: 'Pending',
    bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    dot: 'bg-amber-400',
  },
};

export const StatBadge = ({ status = 'PENDING', size = 'md' }) => {
  const config = STATUS_CONFIGS[status?.toUpperCase()] || STATUS_CONFIGS.PENDING;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${config.bg} ${sizeClasses}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
};
