import React, { useState, useEffect } from 'react';
import {
  ArrowRightLeft,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  AlertTriangle,
  Clock,
  Sparkles,
  MapPin,
  RefreshCw,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import OverrideModal from '../components/OverrideModal';

export default function RecommendationsPage({ activeRole }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Expanded card tracking for evidence
  const [expandedCards, setExpandedCards] = useState({});

  // Override modal state
  const [selectedRecForOverride, setSelectedRecForOverride] = useState(null);
  const [isOverrideModalOpen, setIsOverrideModalOpen] = useState(false);
  const [isSubmittingOverride, setIsSubmittingOverride] = useState(false);

  // Success toast
  const [toastMessage, setToastMessage] = useState('');

  const fetchRecommendations = () => {
    setLoading(true);
    api.getRecommendations({
      priority: priorityFilter,
      status: statusFilter,
    })
      .then((data) => {
        setRecommendations(data);
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
    fetchRecommendations();
  }, [priorityFilter, statusFilter]);

  const toggleExpand = (id) => {
    setExpandedCards((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 4000);
  };

  const handleApprove = (rec) => {
    api.approveRecommendation(rec.recommendation_id, {
      userRole: activeRole,
      reason: 'Clinical transfer confirmed by authorized staff.',
    })
      .then(() => {
        showToast(`Transfer for batch ${rec.batch_id} approved.`);
        // Update local state immediately
        setRecommendations((prev) =>
          prev.map((r) =>
            r.recommendation_id === rec.recommendation_id ? { ...r, status: 'APPROVED' } : r
          )
        );
      })
      .catch((err) => alert(err.message));
  };

  const handleReject = (rec) => {
    api.rejectRecommendation(rec.recommendation_id, {
      userRole: activeRole,
      reason: 'Clinical transfer rejected after pharmacist review.',
    })
      .then(() => {
        showToast(`Transfer for batch ${rec.batch_id} rejected.`);
        setRecommendations((prev) =>
          prev.map((r) =>
            r.recommendation_id === rec.recommendation_id ? { ...r, status: 'REJECTED' } : r
          )
        );
      })
      .catch((err) => alert(err.message));
  };

  const handleOpenOverride = (rec) => {
    setSelectedRecForOverride(rec);
    setIsOverrideModalOpen(true);
  };

  const handleSubmitOverride = (overrideData) => {
    if (!selectedRecForOverride) return;
    setIsSubmittingOverride(true);
    api.overrideRecommendation(selectedRecForOverride.recommendation_id, overrideData)
      .then(() => {
        showToast(`Override recorded for batch ${selectedRecForOverride.batch_id}.`);
        setRecommendations((prev) =>
          prev.map((r) =>
            r.recommendation_id === selectedRecForOverride.recommendation_id
              ? { ...r, status: 'OVERRIDDEN' }
              : r
          )
        );
        setIsOverrideModalOpen(false);
      })
      .catch((err) => alert(err.message))
      .finally(() => {
        setIsSubmittingOverride(false);
      });
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-xl border border-slate-700 flex items-center space-x-2.5 text-xs font-semibold animate-in slide-in-from-bottom-4 duration-150">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Stock Redistribution Recommendations</h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-brand-50 text-brand-700 border border-brand-200">
              Explainable AI
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Rule-based suggestions to route near-expiry surpluses to eligible specialty clinics. Every action requires human approval.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-3">
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="text-xs font-semibold rounded-lg border border-slate-300 px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="All">All Priorities</option>
            <option value="HIGH PRIORITY">High Priority (80-100)</option>
            <option value="MEDIUM PRIORITY">Medium Priority (60-79)</option>
            <option value="LOW PRIORITY">Low Priority (40-59)</option>
            <option value="NO ACTION">No Action (&lt;40)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs font-semibold rounded-lg border border-slate-300 px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="All">All Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="OVERRIDDEN">Overridden</option>
            <option value="BLOCKED">Blocked (Safety)</option>
          </select>

          <button
            onClick={fetchRecommendations}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors"
            title="Refresh recommendations"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Recommendations Cards List */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-16 space-y-3">
          <RefreshCw className="w-8 h-8 text-brand-600 animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Evaluating clinical redistribution rules...</p>
        </div>
      ) : error ? (
        <div className="p-8 text-center text-rose-600 text-xs bg-rose-50 rounded-xl border border-rose-200">{error}</div>
      ) : recommendations.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-2">
          <Info className="w-8 h-8 text-slate-400 mx-auto" />
          <p className="text-sm font-semibold text-slate-800">No recommendations match the selected filters.</p>
          <p className="text-xs text-slate-400">Try changing the priority or status filter above.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => {
            const isExpanded = !!expandedCards[rec.recommendation_id];
            const isPending = rec.status === 'PENDING' || rec.status === 'WARNING';
            const isBlocked = rec.status === 'BLOCKED';

            const priorityBadgeClass = {
              'HIGH PRIORITY': 'bg-rose-50 text-rose-700 border-rose-200',
              'MEDIUM PRIORITY': 'bg-amber-50 text-amber-700 border-amber-200',
              'LOW PRIORITY': 'bg-emerald-50 text-emerald-700 border-emerald-200',
              'NO ACTION': 'bg-slate-100 text-slate-600 border-slate-200',
            }[rec.priority] || 'bg-slate-100 text-slate-600 border-slate-200';

            const confidenceBadgeClass = {
              'HIGH CONFIDENCE': 'bg-emerald-50 text-emerald-700 border-emerald-200',
              'MEDIUM CONFIDENCE': 'bg-amber-50 text-amber-700 border-amber-200',
              'LOW CONFIDENCE': 'bg-rose-50 text-rose-700 border-rose-200',
              'BLOCKED': 'bg-slate-200 text-slate-700 border-slate-300',
            }[rec.confidence_level] || 'bg-slate-100 text-slate-700';

            const statusBadgeClass = {
              APPROVED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
              REJECTED: 'bg-rose-100 text-rose-800 border-rose-300',
              OVERRIDDEN: 'bg-amber-100 text-amber-800 border-amber-300',
              PENDING: 'bg-blue-50 text-blue-700 border-blue-200',
              WARNING: 'bg-amber-50 text-amber-700 border-amber-200',
              BLOCKED: 'bg-slate-100 text-slate-600 border-slate-200',
            }[rec.status] || 'bg-slate-100 text-slate-700';

            return (
              <div
                key={rec.recommendation_id}
                className={`bg-white rounded-2xl border transition-all shadow-sm ${
                  isBlocked ? 'border-slate-200 opacity-80' : 'border-slate-200 hover:border-brand-300'
                }`}
              >
                {/* Header Row */}
                <div className="p-5 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-slate-100">
                  <div className="flex items-start sm:items-center space-x-3.5">
                    <div className="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 flex flex-col items-center justify-center flex-shrink-0">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Score</span>
                      <span className="text-base font-extrabold text-slate-900 leading-none">{rec.risk_score}</span>
                    </div>

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">{rec.batch_id}</span>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${priorityBadgeClass}`}>
                          {rec.priority}
                        </span>
                        <span className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${confidenceBadgeClass}`}>
                          {rec.confidence_level} ({rec.confidence}%)
                        </span>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded border uppercase ${statusBadgeClass}`}>
                          {rec.status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-600">
                        <strong className="text-slate-800">{rec.medicine_code}</strong> — {rec.medicine_name}
                      </div>
                    </div>
                  </div>

                  {/* Route & Quantity Summary */}
                  <div className="flex flex-wrap items-center gap-4 text-xs">
                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex items-center space-x-2">
                      <MapPin className="w-3.5 h-3.5 text-brand-600" />
                      <span className="font-bold text-slate-800">{rec.source_location}</span>
                      <ArrowRightLeft className="w-3 h-3 text-slate-400" />
                      <span className="font-bold text-brand-700">{rec.destination_location}</span>
                    </div>

                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                      <span className="text-slate-500">Recommended Transfer: </span>
                      <strong className="text-slate-900 text-sm font-bold">
                        {rec.recommended_transfer_quantity}
                      </strong>{' '}
                      <span className="text-slate-500">/ {rec.current_quantity} units</span>
                    </div>

                    <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                      <span className="text-slate-500">Expires: </span>
                      <strong className="text-rose-700 font-bold">{rec.days_to_expiry}d left</strong>
                    </div>
                  </div>
                </div>

                {/* Explanation Rationale Narrative */}
                <div className="p-5 bg-slate-50/50 space-y-3">
                  <div className="text-xs leading-relaxed text-slate-700 bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-xs flex items-start space-x-2.5">
                    <Info className="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-900">Clinical Rationale: </span>
                      {rec.explanation}
                    </div>
                  </div>

                  {/* Expandable Evidence Breakdown */}
                  {isExpanded && (
                    <div className="p-4 bg-white rounded-xl border border-slate-200 space-y-3 text-xs animate-in fade-in duration-100">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                        Evidence Breakdown & Multi-Factor Scoring
                      </span>

                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 pt-1">
                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] text-slate-400 font-bold uppercase">Expiry Urgency (35%)</div>
                          <div className="font-bold text-slate-800 text-xs mt-0.5">{rec.evidence?.expiry_urgency}</div>
                          <div className="text-[10px] text-slate-500">Score: {rec.expiry_score}/100</div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] text-slate-400 font-bold uppercase">Source Surplus (25%)</div>
                          <div className="font-bold text-slate-800 text-xs mt-0.5">{rec.evidence?.source_surplus}</div>
                          <div className="text-[10px] text-slate-500">Score: {rec.surplus_score}/100</div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] text-slate-400 font-bold uppercase">Destination Demand (25%)</div>
                          <div className="font-bold text-slate-800 text-xs mt-0.5">{rec.evidence?.destination_demand}</div>
                          <div className="text-[10px] text-slate-500">Score: {rec.demand_score}/100</div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] text-slate-400 font-bold uppercase">Location Logistics (10%)</div>
                          <div className="font-bold text-slate-800 text-xs mt-0.5">{rec.evidence?.distance_feasibility}</div>
                          <div className="text-[10px] text-slate-500">Score: {rec.location_score}/100</div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                          <div className="text-[10px] text-slate-400 font-bold uppercase">Data Quality (5%)</div>
                          <div className="font-bold text-slate-800 text-xs mt-0.5">{rec.evidence?.data_quality}</div>
                          <div className="text-[10px] text-slate-500">Score: {rec.data_quality_score}/100</div>
                        </div>
                      </div>

                      {/* Triggered Rules List */}
                      {rec.evidence?.rules_triggered && rec.evidence.rules_triggered.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-100">
                          <span className="text-[11px] font-bold text-slate-600 block mb-1.5">Rules Triggered:</span>
                          <ul className="space-y-1">
                            {rec.evidence.rules_triggered.map((rule, idx) => (
                              <li key={idx} className="text-slate-600 flex items-start space-x-1.5 text-[11px]">
                                <span className="text-brand-600 font-bold">•</span>
                                <span>{rule}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Actions & Evidence Toggle Bar */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-2">
                    <button
                      onClick={() => toggleExpand(rec.recommendation_id)}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-brand-600 hover:text-brand-700"
                    >
                      <span>{isExpanded ? 'Hide Evidence Breakdown' : 'Show Evidence & Scoring Breakdown'}</span>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {/* Human confirmation buttons */}
                    <div className="flex items-center space-x-2">
                      {isPending && !isBlocked && (
                        <>
                          <button
                            onClick={() => handleApprove(rec)}
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition-colors"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve</span>
                          </button>

                          <button
                            onClick={() => handleReject(rec)}
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>

                          <button
                            onClick={() => handleOpenOverride(rec)}
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg transition-colors"
                          >
                            <AlertOctagon className="w-3.5 h-3.5" />
                            <span>Override</span>
                          </button>
                        </>
                      )}

                      {!isPending && !isBlocked && (
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-slate-500 font-medium">Decision finalized:</span>
                          <span className={`text-xs font-bold px-2 py-0.5 rounded border uppercase ${statusBadgeClass}`}>
                            {rec.status}
                          </span>
                          <button
                            onClick={() => handleOpenOverride(rec)}
                            className="text-xs text-slate-500 hover:text-slate-800 underline ml-2"
                          >
                            Revise Decision
                          </button>
                        </div>
                      )}

                      {isBlocked && (
                        <div className="flex items-center space-x-1 text-xs text-slate-500 italic">
                          <AlertTriangle className="w-3.5 h-3.5 text-slate-400" />
                          <span>Blocked by clinical safety constraint. Transfer forbidden.</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Override Modal */}
      <OverrideModal
        recommendation={selectedRecForOverride}
        isOpen={isOverrideModalOpen}
        onClose={() => setIsOverrideModalOpen(false)}
        onSubmit={handleSubmitOverride}
        isSubmitting={isSubmittingOverride}
        activeRole={activeRole}
      />
    </div>
  );
}
