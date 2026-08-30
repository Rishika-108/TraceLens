import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiGrid,
  FiHardDrive,
  FiCpu,
  FiFileText,
  FiFolder,
  FiChevronDown,
  FiX,
} from 'react-icons/fi';
import { useCase } from '../../context/CaseContext';

export const Sidebar = ({ mobileMenuOpen, setMobileMenuOpen }) => {
  const { cases, activeCase, selectCase } = useCase();

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
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileMenuOpen && (
        <div
          onClick={() => setMobileMenuOpen?.(false)}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-64 bg-slate-950/95 md:bg-transparent glass-panel border-r border-slate-800/80 min-h-[calc(100vh-61px)] p-4 flex flex-col justify-between transition-transform duration-300 ease-in-out ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="space-y-6">
          {/* Mobile Header with Close Button */}
          <div className="flex md:hidden items-center justify-between pb-3 border-b border-slate-800">
            <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
              Navigation Menu
            </span>
            <button
              onClick={() => setMobileMenuOpen?.(false)}
              className="p-1.5 rounded-lg bg-slate-900 text-slate-400 hover:text-slate-200"
            >
              <FiX className="w-5 h-5" />
            </button>
          </div>

          {/* Mobile Active Case Selector */}
          {activeCase && (
            <div className="md:hidden p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1.5 uppercase">
                <FiFolder className="text-cyan-400" />
                Active Investigation:
              </div>
              <div className="relative">
                <select
                  value={activeCase.id}
                  onChange={(e) => {
                    const selected = cases.find((c) => c.id === e.target.value);
                    if (selected) selectCase(selected);
                  }}
                  className="w-full appearance-none bg-slate-950 border border-slate-700/80 text-slate-200 text-xs font-semibold py-2 pl-3 pr-8 rounded-lg cursor-pointer focus:outline-none focus:border-cyan-500 transition-colors truncate"
                >
                  {cases.map((c) => (
                    <option key={c.id} value={c.id} className="bg-slate-900 text-slate-200">
                      {c.title}
                    </option>
                  ))}
                </select>
                <FiChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none w-3.5 h-3.5" />
              </div>
            </div>
          )}

          {/* Navigation Section */}
          <div>
            <div className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-500 px-3 mb-2">
              Forensic Workspaces
            </div>
            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isDisabled = item.requiresCase && !activeCase;

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen?.(false)}
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
        </div>

        {/* Footer info in desktop sidebar */}
        <div className="pt-4 border-t border-slate-800/80 text-[11px] font-mono text-slate-500 text-left">
          <div>Status: <span className="text-emerald-400 font-semibold">Ready</span></div>
          <div className="text-[10px] text-slate-600 mt-0.5">PostgreSQL pgvector Engine</div>
        </div>
      </aside>
    </>
  );
};
