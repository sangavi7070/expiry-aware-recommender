import React, { useState, useEffect } from 'react';
import { Pill, RefreshCw, ShieldAlert, CheckCircle2, UserCheck } from 'lucide-react';
import { api } from '../services/api';

export default function Navbar({ onResetDemoClick, activeRole, setActiveRole }) {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    let mounted = true;
    api.getHealth()
      .then(() => {
        if (mounted) setBackendStatus('online');
      })
      .catch(() => {
        if (mounted) setBackendStatus('offline');
      });
    return () => { mounted = false; };
  }, []);

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Subtitle */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <Pill className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-slate-900">ExpiryAware</span>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200">
                  Clinical v1.0
                </span>
              </div>
              <p className="hidden md:block text-xs text-slate-500 font-medium">
                Responsible inventory intelligence for temperature-sensitive medicines
              </p>
            </div>
          </div>

          {/* Right Action Controls */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            {/* System Connectivity Pill */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-slate-50 border-slate-200">
              {backendStatus === 'online' ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-slate-700">API Connected</span>
                </>
              ) : backendStatus === 'checking' ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                  <span className="text-slate-500">Connecting...</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  <span className="text-rose-600 font-semibold">Offline</span>
                </>
              )}
            </div>

            {/* Role Switcher */}
            <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
              <UserCheck className="w-3.5 h-3.5 text-brand-600" />
              <span className="text-slate-400">Role:</span>
              <select
                value={activeRole}
                onChange={(e) => setActiveRole(e.target.value)}
                className="bg-transparent font-semibold text-slate-800 focus:outline-none cursor-pointer"
              >
                <option value="Pharmacist">Pharmacist</option>
                <option value="Inventory Manager">Inventory Manager</option>
                <option value="Clinic Administrator">Clinic Administrator</option>
                <option value="Clinical Lead">Clinical Lead</option>
              </select>
            </div>

            {/* Reset Demo Data Button */}
            <button
              onClick={onResetDemoClick}
              title="Re-seed database to deterministic synthetic baseline"
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
              <span>Reset Demo Data</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
