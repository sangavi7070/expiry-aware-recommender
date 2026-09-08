import React, { useState, useEffect } from 'react';
import {
  Activity,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  FileQuestion,
  RefreshCw,
  Info
} from 'lucide-react';
import { api } from '../services/api';

export default function DataQualityPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchQuality = () => {
    setLoading(true);
    api.getDataQuality()
      .then((data) => {
        setReport(data);
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
    fetchQuality();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Scanning inventory dataset for clinical integrity issues...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-8 text-center text-rose-600 bg-rose-50 rounded-2xl border border-rose-200">
        <p className="text-sm font-bold">Failed to load data quality report: {error}</p>
      </div>
    );
  }

  const flaggedCount = report.flagged_batches?.length || 0;

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Data Integrity</h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-cyan-50 text-cyan-700 border border-cyan-200">
              Input Validation
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Proactive data quality surveillance to ensure safety constraints are met before generating redistribution recommendations.
          </p>
        </div>

        <button
          onClick={fetchQuality}
          className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors"
          title="Refresh quality scan"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Primary Banner */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-brand-600" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Overall Data Quality Index</span>
          </div>
          <div className="text-4xl font-extrabold text-slate-900">
            {report.overall_quality_score}%
          </div>
          <p className="text-xs text-slate-500">
            Weighted composite score across batch identifiers, cold-chain metadata, expiry formats, and demand metrics.
          </p>
        </div>

        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 max-w-md w-full text-xs space-y-2">
          <div className="flex items-center space-x-2 font-bold text-slate-800">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span>Clinical Data Governance Advisory:</span>
          </div>
          <p className="text-slate-600 leading-relaxed">
            <strong>{flaggedCount} records</strong> require clinical data review before they can be used for optimal redistribution recommendations. Missing expiry dates and non-positive stock counts are strictly BLOCKED from recommendation.
          </p>
        </div>
      </div>

      {/* Health Cards Breakdown */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-slate-400">Total Records</span>
          <div className="text-xl font-bold text-slate-900 mt-1">{report.total_records}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Monitored batches</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-emerald-600">Complete & Valid</span>
          <div className="text-xl font-bold text-emerald-700 mt-1">{report.complete_records}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Ready for transfer</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-rose-600">Missing Expiry</span>
          <div className="text-xl font-bold text-rose-700 mt-1">{report.missing_expiry_count}</div>
          <div className="text-[11px] text-rose-600 font-semibold mt-0.5">BLOCKED</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-amber-600">Missing Demand</span>
          <div className="text-xl font-bold text-amber-700 mt-1">{report.missing_demand_count}</div>
          <div className="text-[11px] text-amber-600 font-semibold mt-0.5">WARNING</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-rose-600">Invalid Quantity</span>
          <div className="text-xl font-bold text-rose-700 mt-1">{report.invalid_quantity_count}</div>
          <div className="text-[11px] text-rose-600 font-semibold mt-0.5">BLOCKED</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-[10px] font-bold uppercase text-amber-600">Low Quality (&lt;75%)</span>
          <div className="text-xl font-bold text-amber-700 mt-1">{report.low_quality_count}</div>
          <div className="text-[11px] text-amber-600 font-semibold mt-0.5">Review needed</div>
        </div>
      </div>

      {/* Flagged Records Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Flagged Records Requiring Data Steward Review</h2>
            <p className="text-xs text-slate-500">Batches flagged by validation engine for missing fields, expired status, or degraded quality.</p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-200 text-slate-700">
            {report.flagged_batches?.length || 0} Flagged
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-700 font-bold uppercase text-[11px]">
                <th className="p-4">Batch ID</th>
                <th className="p-4">Medicine</th>
                <th className="p-4">Clinic Location</th>
                <th className="p-4">Validation Issue & Clinical Impact</th>
                <th className="p-4 text-center">Severity</th>
                <th className="p-4 text-right">Data Quality</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {report.flagged_batches?.map((b) => (
                <tr key={b.batch_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-4 font-mono font-bold text-slate-900">{b.batch_id}</td>
                  <td className="p-4 font-semibold text-slate-800">{b.medicine_code}</td>
                  <td className="p-4 text-slate-600">{b.source_location}</td>
                  <td className="p-4 max-w-md text-slate-700 leading-relaxed font-medium">
                    {b.issue}
                  </td>
                  <td className="p-4 text-center">
                    <span
                      className={`inline-block px-2.5 py-1 rounded text-[10px] font-extrabold uppercase border ${
                        b.severity === 'BLOCKED'
                          ? 'bg-rose-50 text-rose-700 border-rose-200'
                          : 'bg-amber-50 text-amber-700 border-amber-200'
                      }`}
                    >
                      {b.severity}
                    </span>
                  </td>
                  <td className="p-4 text-right font-mono font-bold text-slate-800">
                    {b.data_quality_score}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
