import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FiShield,
  FiFolder,
  FiChevronDown,
  FiLogOut,
  FiMenu,
  FiX,
} from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { useCase } from '../../context/CaseContext';

export const Navbar = ({ mobileMenuOpen, setMobileMenuOpen }) => {
  const { user, logout } = useAuth();
  const { cases, activeCase, selectCase } = useCase();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-4 sm:px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Brand & Mobile Hamburger */}
        <div className="flex items-center gap-3 sm:gap-6">
          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen?.(!mobileMenuOpen)}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 md:hidden hover:text-cyan-400 focus:outline-none transition-colors"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <FiX className="w-5 h-5" /> : <FiMenu className="w-5 h-5" />}
          </button>

          <Link to="/" className="flex items-center gap-2.5 sm:gap-3 group">
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all">
              <FiShield className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div>
              <span className="text-lg sm:text-xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300 bg-clip-text text-transparent">
                TraceLens
              </span>
              <span className="hidden sm:inline-block ml-2 text-[10px] uppercase font-mono tracking-widest px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
                v1.0
              </span>
            </div>
          </Link>

          {/* Active Case Selector Dropdown */}
          {activeCase && (
            <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-800">
              <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
                <FiFolder className="text-cyan-400 w-3.5 h-3.5" />
                Active Case:
              </span>
              <div className="relative group">
                <select
                  value={activeCase.id}
                  onChange={(e) => {
                    const selected = cases.find((c) => c.id === e.target.value);
                    if (selected) selectCase(selected);
                  }}
                  className="appearance-none bg-slate-900/80 hover:bg-slate-850 border border-slate-700/80 text-slate-200 text-xs font-semibold py-1.5 pl-3 pr-8 rounded-lg cursor-pointer focus:outline-none focus:border-cyan-500 transition-colors max-w-[220px] truncate"
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
        </div>

        {/* Right Actions: User Profile & Logout */}
        <div className="flex items-center gap-2 sm:gap-3">
          {user && (
            <div className="flex items-center gap-2 sm:gap-2.5 px-2.5 sm:px-3 py-1.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg bg-cyan-950/80 border border-cyan-800/50 flex items-center justify-center text-cyan-400 text-xs font-bold font-mono">
                {user.username.slice(0, 2).toUpperCase()}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-semibold text-slate-200 leading-none">
                  {user.username}
                </div>
                <div className="text-[10px] text-cyan-400 font-mono leading-tight mt-0.5">
                  {user.role}
                </div>
              </div>
            </div>
          )}

          <button
            onClick={handleLogout}
            className="p-2 sm:px-3 sm:py-1.5 rounded-xl bg-slate-900/60 hover:bg-rose-500/10 border border-slate-800 hover:border-rose-500/30 text-slate-400 hover:text-rose-400 text-xs font-medium transition-all flex items-center gap-1.5"
            title="Log Out Session"
          >
            <FiLogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};
