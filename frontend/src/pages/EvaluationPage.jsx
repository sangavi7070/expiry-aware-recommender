import React, { useState, useEffect } from 'react';
import {
  FlaskConical,
  TrendingUp,
  AlertOctagon,
  ShieldCheck,
  CheckCircle2,
  Users,
  RefreshCw,
  Star,
  Info,
  ArrowRight,
  TrendingDown
} from 'lucide-react';
import { api } from '../services/api';

export default function EvaluationPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEvaluation = () => {
    setLoading(true);
    api.getEvaluation()
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
    fetchEvaluation();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4">
        <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Running measurable baseline simulation and metric comparison...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-8 text-center text-rose-600 bg-rose-50 rounded-2xl border border-rose-200">
        <p className="text-sm font-bold">Failed to load evaluation metrics: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Empirical System Evaluation</h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-200">
              Measurable Experiment
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic benchmark comparing standard clinic FIFO local usage against the ExpiryAware redistribution engine.
          </p>
        </div>

        <button
          onClick={fetchEvaluation}
          className="inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors shadow-xs"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
          <span>Re-run Simulation</span>
        </button>
      </div>

      {/* Primary Impact Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-emerald-500">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Net Waste Avoided</div>
          <div className="text-2xl font-black text-slate-900 mt-1">
            ${report.waste_avoided_amount?.toLocaleString()}
          </div>
          <div className="mt-1 text-xs text-emerald-700 font-semibold flex items-center space-x-1">
            <TrendingDown className="w-3.5 h-3.5" />
            <span>{report.waste_avoided_percentage}% reduction in losses</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-brand-500">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Stock Transferred</div>
          <div className="text-2xl font-black text-brand-700 mt-1">
            ${report.proposed_summary?.stock_transferred_protected?.toLocaleString()}
          </div>
          <div className="mt-1 text-xs text-slate-500">Intelligently reallocated</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-cyan-500">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Recommendation Coverage</div>
          <div className="text-2xl font-black text-cyan-700 mt-1">
            {report.recommendation_coverage}%
          </div>
          <div className="mt-1 text-xs text-slate-500">Surplus batches routed</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-amber-500">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Human Override Rate</div>
          <div className="text-2xl font-black text-amber-700 mt-1">
            {report.human_override_rate}%
          </div>
          <div className="mt-1 text-xs text-slate-500">Clinical exceptions captured</div>
        </div>
      </div>

      {/* Metric Comparison Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 bg-slate-50 border-b border-slate-200">
          <h2 className="text-base font-bold text-slate-900">Baseline vs Proposed System Performance</h2>
          <p className="text-xs text-slate-500">
            Real data simulation comparing standard FIFO (First-In, First-Out local consumption) with the ExpiryAware recommendation engine.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-700 font-bold uppercase text-[11px]">
                <th className="p-4">Evaluation Metric</th>
                <th className="p-4 text-right">Baseline (FIFO)</th>
                <th className="p-4 text-right">Target Benchmark</th>
                <th className="p-4 text-right">Measured (ExpiryAware)</th>
                <th className="p-4 text-right">Measured Difference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {report.comparison_table?.map((row, idx) => {
                const isPositiveGood = row.metric.includes('used') || row.metric.includes('transferred') || row.metric.includes('avoided') || row.metric.includes('coverage');
                const isDiffFavorable = isPositiveGood ? row.difference > 0 : row.difference < 0;

                return (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-4 font-semibold text-slate-900">
                      {row.metric}
                    </td>
                    <td className="p-4 text-right font-mono text-slate-600">
                      {row.unit === '$' ? `$${row.baseline?.toLocaleString()}` : `${row.baseline}${row.unit}`}
                    </td>
                    <td className="p-4 text-right font-mono text-slate-500">
                      {row.unit === '$' ? `$${row.target?.toLocaleString()}` : `${row.target}${row.unit}`}
                    </td>
                    <td className="p-4 text-right font-mono font-bold text-slate-900">
                      {row.unit === '$' ? `$${row.measured?.toLocaleString()}` : `${row.measured}${row.unit}`}
                    </td>
                    <td className="p-4 text-right font-mono font-bold">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] ${
                          isDiffFavorable
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {row.difference > 0 ? `+` : ``}
                        {row.unit === '$' ? `$${row.difference?.toLocaleString()}` : `${row.difference}${row.unit}`}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Error Analysis & Uncertainty Profile */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center space-x-2">
          <AlertOctagon className="w-5 h-5 text-amber-600" />
          <h2 className="text-base font-bold text-slate-900">Error Analysis & Uncertainty Edge Cases</h2>
        </div>
        <p className="text-xs text-slate-500">
          Responsible AI inspection of cases where recommendations were blocked, degraded in confidence, or modified by clinical staff.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {report.error_analysis?.map((item, idx) => (
            <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900">{item.category}</span>
                <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-white text-slate-700 border border-slate-200">
                  {item.count} occurrences
                </span>
              </div>
              <p className="text-slate-600 leading-relaxed">{item.description}</p>
              <div className="pt-2 border-t border-slate-200/80 text-slate-500 italic">
                <strong className="text-slate-700 not-italic">Clinical Scenario: </strong>
                {item.example}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Synthetic Stakeholder Validation */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-brand-600" />
            <h2 className="text-base font-bold text-slate-900">Synthetic Stakeholder Validation</h2>
          </div>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
            Synthetic Validation Study
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Simulated evaluation across multi-disciplinary hospital roles assessing interpretability, safety constraints, and workflow utility.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
          {report.stakeholder_validation?.map((item, idx) => (
            <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-brand-800 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                  {item.role}
                </span>
                <div className="flex items-center space-x-1 font-bold text-slate-900">
                  <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
                  <span>{item.score} / 5.0</span>
                </div>
              </div>
              <div className="font-semibold text-slate-800">{item.question}</div>
              <p className="text-slate-600 text-[11px] italic bg-white p-2.5 rounded-lg border border-slate-200">
                "{item.feedback}"
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
