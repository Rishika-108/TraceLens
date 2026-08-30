import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider, useAuth } from './context/AuthContext';
import { CaseProvider } from './context/CaseContext';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Case } from './pages/Case';
import { Investigation } from './pages/Investigation';
import { Report } from './pages/Report';

// Protected Route Guard
const ProtectedLayout = () => {
  const { isAuthenticated, loading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-xs font-mono text-cyan-400">
        Authenticating Investigator Session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <CaseProvider>
      <div className="min-h-screen bg-slate-950 bg-forensic-grid flex flex-col">
        <Navbar mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />
        <div className="flex-1 flex overflow-hidden relative">
          <Sidebar mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />
          <main className="flex-1 overflow-y-auto p-3 sm:p-6 lg:p-8 w-full">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/case" element={<Case />} />
              <Route path="/investigation" element={<Investigation />} />
              <Route path="/report" element={<Report />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </CaseProvider>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </BrowserRouter>
      <ToastContainer
        position="bottom-right"
        theme="dark"
        toastClassName="bg-slate-900 border border-slate-800 text-slate-200"
      />
    </AuthProvider>
  );
}
