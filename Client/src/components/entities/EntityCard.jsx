import React from 'react';
import {
  FiUser,
  FiPhone,
  FiMail,
  FiKey,
  FiGlobe,
  FiMapPin,
  FiBriefcase,
  FiCopy,
  FiCheck,
} from 'react-icons/fi';

const ENTITY_CONFIG = {
  PERSON: {
    icon: FiUser,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/30',
    label: 'Person / Suspect',
  },
  PHONE: {
    icon: FiPhone,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    label: 'Phone Number',
  },
  EMAIL: {
    icon: FiMail,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/30',
    label: 'Email Address',
  },
  CRYPTO_ADDRESS: {
    icon: FiKey,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
    label: 'Crypto Wallet',
  },
  IP_ADDRESS: {
    icon: FiGlobe,
    color: 'text-violet-400',
    bg: 'bg-violet-500/10 border-violet-500/30',
    label: 'IP Address',
  },
  ORG: {
    icon: FiBriefcase,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/30',
    label: 'Organization',
  },
  LOCATION: {
    icon: FiMapPin,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
    label: 'Location / POI',
  },
  DOMAIN: {
    icon: FiGlobe,
    color: 'text-teal-400',
    bg: 'bg-teal-500/10 border-teal-500/30',
    label: 'Domain / Host',
  },
};

export const EntityCard = ({ entity, onCopy, isCopied }) => {
  const config = ENTITY_CONFIG[entity.entity_type] || {
    icon: FiUser,
    color: 'text-slate-400',
    bg: 'bg-slate-500/10 border-slate-500/30',
    label: entity.entity_type,
  };
  const Icon = config.icon;

  return (
    <div className="glass-panel glass-panel-hover p-4 rounded-2xl border border-slate-800 text-left flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span
            className={`inline-flex items-center gap-1.5 text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${config.bg} ${config.color}`}
          >
            <Icon className="w-3 h-3" />
            {config.label}
          </span>
          <button
            onClick={() => onCopy(entity.value)}
            className="p-1 rounded-lg text-slate-500 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
            title="Copy Value"
          >
            {isCopied ? <FiCheck className="w-3.5 h-3.5 text-emerald-400" /> : <FiCopy className="w-3.5 h-3.5" />}
          </button>
        </div>
        <div className="text-sm font-semibold font-mono text-slate-100 break-all">
          {entity.value}
        </div>
      </div>

      {entity.artifact_id && (
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 text-[10px] font-mono text-slate-500 truncate">
          Linked Art: #{entity.artifact_id.slice(0, 8)}
        </div>
      )}
    </div>
  );
};
