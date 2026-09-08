import React from 'react';
import {
  LayoutDashboard,
  Package,
  ArrowRightLeft,
  FlaskConical,
  ClipboardList,
  Activity,
  HeartHandshake
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'inventory', label: 'Inventory', icon: Package },
  { id: 'recommendations', label: 'Recommendations', icon: ArrowRightLeft },
  { id: 'evaluation', label: 'Evaluation & Baseline', icon: FlaskConical },
  { id: 'audit', label: 'Audit Log', icon: ClipboardList },
  { id: 'data-quality', label: 'Data Quality', icon: Activity },
  { id: 'responsible-ai', label: 'Responsible AI', icon: HeartHandshake },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex-shrink-0 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)] border-r border-slate-800">
      <div className="py-5 px-3 space-y-1">
        <div className="px-3 pb-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Clinical Operations
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20 font-semibold'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Safety & Protocol Footer */}
      <div className="p-4 m-3 rounded-xl bg-slate-800/60 border border-slate-700/50 text-xs text-slate-400">
        <div className="flex items-center space-x-1.5 text-slate-200 font-semibold mb-1">
          <span className="w-2 h-2 rounded-full bg-brand-400"></span>
          <span>Clinical Governance</span>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-400">
          Redistributions require authorized pharmacist confirmation. No autonomous dispatch.
        </p>
      </div>
    </aside>
  );
}
