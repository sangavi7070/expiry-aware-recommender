import React, { useState, useEffect } from 'react';
import { ClipboardList, CheckCircle2, XCircle, AlertOctagon, RefreshCw, Calendar, UserCheck } from 'lucide-react';
import { api } from '../services/api';

export default function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionFilter, setActionFilter] = useState('All');

  const fetchAudit = () => {
    setLoading(true);
    api.getAuditLog(actionFilter)
      .then((data) => {
        setLogs(data);
        setError(null);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAudit();
  }, [actionFilter]);

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Clinical Audit Log</h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
              Immutable Governance Trail
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Complete cryptographic audit trail of all pharmacist confirmations, rejections, and clinical overrides.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="text-xs font-semibold rounded-lg border border-slate-300 px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="All">All Actions</option>
            <option value="APPROVED">Approved Only</option>
            <option value="REJECTED">Rejected Only</option>
            <option value="OVERRIDDEN">Overridden Only</option>
          </select>

          <button
            onClick={fetchAudit}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors"
            title="Refresh logs"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-16 space-y-3">
            <RefreshCw className="w-6 h-6 text-brand-600 animate-spin" />
            <p className="text-xs text-slate-500 font-medium">Retrieving audit log entries...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-xs bg-rose-50">{error}</div>
        ) : logs.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-2">
            <ClipboardList className="w-8 h-8 text-slate-400 mx-auto" />
            <p className="text-sm font-semibold text-slate-800">No audit events found for this filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase text-[11px]">
                  <th className="p-4">Audit ID</th>
                  <th className="p-4">Action</th>
                  <th className="p-4">Recommendation / Batch</th>
                  <th className="p-4">Staff Role</th>
                  <th className="p-4">Reason & Notes</th>
                  <th className="p-4 text-right">Timestamp (UTC)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((log) => {
                  const actionClass = {
                    APPROVED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
                    REJECTED: 'bg-rose-50 text-rose-700 border-rose-200',
                    OVERRIDDEN: 'bg-amber-50 text-amber-800 border-amber-200',
                  }[log.action] || 'bg-slate-100 text-slate-700';

                  const Icon = {
                    APPROVED: CheckCircle2,
                    REJECTED: XCircle,
                    OVERRIDDEN: AlertOctagon,
                  }[log.action] || ClipboardList;

                  const formattedDate = new Date(log.timestamp).toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  });

                  return (
                    <tr key={log.audit_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="p-4 font-mono font-bold text-slate-700">{log.audit_id}</td>
                      <td className="p-4">
                        <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold border ${actionClass}`}>
                          <Icon className="w-3.5 h-3.5" />
                          <span>{log.action}</span>
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="font-bold text-slate-900">{log.recommendation_id}</div>
                        {log.batch_id && (
                          <div className="text-[11px] text-slate-500 font-medium">Batch: {log.batch_id}</div>
                        )}
                      </td>
                      <td className="p-4">
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-100 font-semibold text-slate-700 text-[11px]">
                          <UserCheck className="w-3 h-3 text-brand-600" />
                          <span>{log.user_role}</span>
                        </span>
                      </td>
                      <td className="p-4 max-w-md">
                        <div className="font-semibold text-slate-900">{log.reason}</div>
                        {log.notes && (
                          <div className="text-[11px] text-slate-500 mt-0.5 italic">"{log.notes}"</div>
                        )}
                      </td>
                      <td className="p-4 text-right font-mono text-[11px] text-slate-500 whitespace-nowrap">
                        {formattedDate}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
