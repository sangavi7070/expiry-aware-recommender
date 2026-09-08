import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, badge, color = 'blue' }) {
  const colorStyles = {
    blue: {
      iconBg: 'bg-blue-50 text-blue-600 border-blue-200',
      border: 'border-l-blue-500',
    },
    amber: {
      iconBg: 'bg-amber-50 text-amber-600 border-amber-200',
      border: 'border-l-amber-500',
    },
    rose: {
      iconBg: 'bg-rose-50 text-rose-600 border-rose-200',
      border: 'border-l-rose-500',
    },
    emerald: {
      iconBg: 'bg-emerald-50 text-emerald-600 border-emerald-200',
      border: 'border-l-emerald-500',
    },
    cyan: {
      iconBg: 'bg-cyan-50 text-cyan-600 border-cyan-200',
      border: 'border-l-cyan-500',
    },
    purple: {
      iconBg: 'bg-purple-50 text-purple-600 border-purple-200',
      border: 'border-l-purple-500',
    },
  }[color] || {
    iconBg: 'bg-slate-50 text-slate-600 border-slate-200',
    border: 'border-l-slate-500',
  };

  return (
    <div className={`bg-white rounded-xl p-5 border border-slate-200/80 shadow-sm border-l-4 ${colorStyles.border} transition-all hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        {Icon && (
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center border ${colorStyles.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="mt-2 flex items-baseline justify-between">
        <div className="text-2xl font-bold tracking-tight text-slate-900">{value}</div>
        {badge && (
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
}
