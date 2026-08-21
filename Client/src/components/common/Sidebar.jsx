import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiGrid,
  FiHardDrive,
  FiCpu,
  FiFileText,
  FiLayers,
  FiSearch,
} from 'react-icons/fi';
import { useCase } from '../../context/CaseContext';

export const Sidebar = () => {
  const { activeCase } = useCase();

  const navItems = [
    {
      label: 'Case Portfolio',
      path: '/',
      icon: FiGrid,
    },
    {
      label: 'Evidence Hub',
      path: '/case',
      icon: FiHardDrive,
      requiresCase: true,
    },
    {
      label: 'AI Investigation',
      path: '/investigation',
      icon: FiCpu,
      requiresCase: true,
      badge: 'AI',
    },
    {
      label: 'Intelligence Reports',
      path: '/report',
      icon: FiFileText,
      requiresCase: true,
    },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 min-h-[calc(100vh-61px)] p-4 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Navigation Section */}
        <div>
          <div className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-500 px-3 mb-2">
            Navigation
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isDisabled = item.requiresCase && !activeCase;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                      isDisabled
                        ? 'opacity-40 pointer-events-none text-slate-600'
                        : isActive
                        ? 'bg-gradient-to-r from-cyan-500/15 to-indigo-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/40">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Active Case Details Widget */}
        {activeCase && (
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-left">
            <div className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold mb-1 flex items-center gap-1.5">
              <FiLayers className="w-3 h-3" />
              Target Case
            </div>
            <h4 className="text-xs font-semibold text-slate-200 truncate">{activeCase.title}</h4>
            <div className="text-[10px] font-mono text-slate-500 truncate mt-1">
              ID: {activeCase.id}
            </div>
          </div>
        )}
      </div>

      {/* Footer Security Badge */}
      <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 text-left">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] font-mono text-slate-400 font-medium">Chain of Custody Active</span>
        </div>
        <div className="text-[10px] text-slate-600 font-mono mt-1">
          SHA-256 Verified Storage
        </div>
      </div>
    </aside>
  );
};
