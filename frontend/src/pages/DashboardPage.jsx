import React, { useState, useEffect } from 'react';
import {
  Package,
  AlertTriangle,
  ArrowRightLeft,
  ShieldCheck,
  DollarSign,
  Clock,
  TrendingUp,
  RefreshCw,
  AlertOctagon,
  Sparkles
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import MetricCard from '../components/MetricCard';
import { api } from '../services/api';

const PIE_COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'];

export default function DashboardPage({ setActiveTab }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = () => {
    setLoading(true);
    api.getDashboard()
      .then((res) => {
        setData(res);
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
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Aggregating clinic inventory metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 text-center space-y-3">
          <AlertOctagon className="w-10 h-10 text-rose-600 mx-auto" />
          <h3 className="text-base font-bold text-rose-900">Unable to Load Dashboard Data</h3>
          <p className="text-sm text-rose-700">{error}</p>
          <button
            onClick={fetchDashboard}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Clinical Inventory Intelligence</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time monitoring of specialty medicine batches, near-expiry risks, and inter-clinic redistribution opportunities.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('recommendations')}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-sm transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Review Pending Transfers ({data.pending_approvals_count})</span>
          </button>
          <button
            onClick={fetchDashboard}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors"
            title="Refresh dashboard"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Total Batches"
          value={data.total_batches}
          subtitle="Monitored clinic stock"
          icon={Package}
          color="blue"
        />
        <MetricCard
          title="Near-Expiry Batches"
          value={data.near_expiry_batches}
          subtitle="<= 30 days remaining"
          icon={Clock}
          color="rose"
        />
        <MetricCard
          title="Stock At Risk"
          value={`$${(data.stock_at_risk_value / 1000).toFixed(1)}k`}
          subtitle="Critical expiry value"
          icon={AlertTriangle}
          color="amber"
        />
        <MetricCard
          title="Transfers Planned"
          value={data.recommended_transfers_count}
          subtitle="Surplus matched to demand"
          icon={ArrowRightLeft}
          color="cyan"
        />
        <MetricCard
          title="Value Protected"
          value={`$${(data.value_saved_protected / 1000).toFixed(1)}k`}
          subtitle="Preserved from discard"
          icon={ShieldCheck}
          color="emerald"
        />
        <MetricCard
          title="Pending Approval"
          value={data.pending_approvals_count}
          subtitle="Awaiting pharmacist review"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Savings Highlight Banner */}
      <div className="bg-gradient-to-r from-brand-900 to-slate-900 rounded-2xl p-5 text-white shadow-md flex flex-col md:flex-row items-center justify-between gap-4 border border-brand-800">
        <div className="space-y-1 text-center md:text-left">
          <span className="text-[11px] font-bold uppercase tracking-wider text-brand-300">Intelligent Redistribution Impact</span>
          <h2 className="text-lg font-bold">
            ${data.baseline_vs_proposed_savings?.waste_avoided_amount?.toLocaleString()} Projected Waste Prevented
          </h2>
          <p className="text-xs text-slate-300">
            Intelligently routing surplus batches achieves a{' '}
            <strong className="text-emerald-400 font-bold">{data.baseline_vs_proposed_savings?.waste_avoided_percentage}% reduction</strong>{' '}
            in expired medicine losses compared to standalone local FIFO consumption.
          </p>
        </div>
        <button
          onClick={() => setActiveTab('evaluation')}
          className="whitespace-nowrap px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-400 text-white font-semibold text-xs transition-colors shadow-sm"
        >
          View Measurable Evaluation →
        </button>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Stock Value by Location */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Stock Value & Near-Expiry Risk by Clinic</h3>
              <p className="text-xs text-slate-500">Comparison of total held inventory vs stock expiring within 30 days</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.stock_by_location} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="location" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(value) => [`$${Number(value).toLocaleString()}`, '']}
                  contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="total_value" name="Total Stock Value" fill="#0284c7" radius={[4, 4, 0, 0]} />
                <Bar dataKey="at_risk_value" name="At-Risk Value (<=30d)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Expiry Breakdown Donut */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Inventory Expiry Horizon</h3>
              <p className="text-xs text-slate-500">Distribution of batches across clinical urgency tiers</p>
            </div>
          </div>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.near_expiry_breakdown}
                  dataKey="count"
                  nameKey="range_label"
                  cx="50%"
                  cy="50%"
                  outerRadius={85}
                  innerRadius={50}
                  paddingAngle={3}
                  label={({ range_label, count }) => `${count}`}
                >
                  {data.near_expiry_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name, item) => [
                    `${value} batches ($${item.payload.value?.toLocaleString()})`,
                    name,
                  ]}
                  contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Recommendation Priority Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Recommendation Urgency Bands</h3>
              <p className="text-xs text-slate-500">Classification determined by explainable 5-factor scoring engine</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.priority_distribution} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="priority" type="category" tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `${val} batches ($${item.payload.transfer_value?.toLocaleString()} transfer val)`,
                    'Count',
                  ]}
                  contentStyle={{ borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" name="Batches" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Baseline vs Proposed Waste Comparison */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold text-slate-900">Baseline vs Proposed Waste Comparison</h3>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                -74% Waste Reduction
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-6">
              Simulated loss comparison between baseline local consumption and active stock redistribution.
            </p>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-slate-600">Baseline Discarded Waste (FIFO Local Only):</span>
                  <span className="text-rose-600 font-bold">${data.baseline_vs_proposed_savings?.baseline_waste?.toLocaleString()}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div className="bg-rose-500 h-full rounded-full w-full"></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-slate-600">Proposed Discarded Waste (ExpiryAware):</span>
                  <span className="text-emerald-600 font-bold">${data.baseline_vs_proposed_savings?.proposed_waste?.toLocaleString()}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full"
                    style={{
                      width: `${Math.max(
                        (data.baseline_vs_proposed_savings?.proposed_waste /
                          Math.max(data.baseline_vs_proposed_savings?.baseline_waste, 1)) *
                          100,
                        5
                      )}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-100 mt-4 flex items-center justify-between text-xs text-slate-500">
            <span>Deterministic simulation calculated from current synthetic inventory.</span>
            <button
              onClick={() => setActiveTab('evaluation')}
              className="text-brand-600 font-bold hover:text-brand-700"
            >
              Full Breakdown →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
