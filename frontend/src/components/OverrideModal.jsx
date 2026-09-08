import React, { useState } from 'react';
import { AlertOctagon, X, Check, Loader2 } from 'lucide-react';

const OVERRIDE_REASONS = [
  'Demand changed',
  'Stock already allocated',
  'Temperature concern',
  'Transfer not feasible',
  'Data appears incorrect',
  'Other',
];

const ROLES = [
  'Pharmacist',
  'Inventory Manager',
  'Clinic Administrator',
  'Clinical Lead',
];

export default function OverrideModal({ recommendation, isOpen, onClose, onSubmit, isSubmitting, activeRole }) {
  const [reason, setReason] = useState(OVERRIDE_REASONS[0]);
  const [role, setRole] = useState(activeRole || 'Pharmacist');
  const [notes, setNotes] = useState('');
  const [validationError, setValidationError] = useState('');

  if (!isOpen || !recommendation) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!reason || reason.trim() === '') {
      setValidationError('Please select a mandatory clinical override reason.');
      return;
    }
    setValidationError('');
    onSubmit({
      reason,
      userRole: role,
      notes: notes.trim(),
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-lg w-full overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center">
              <AlertOctagon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Clinical Recommendation Override</h3>
              <p className="text-xs text-slate-500">Human-in-the-loop clinical exception handling</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Target Recommendation Context */}
          <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200 text-xs space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Batch ID:</span>
              <span className="font-bold text-slate-800">{recommendation.batch_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Medicine:</span>
              <span className="font-semibold text-slate-800">{recommendation.medicine_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-medium">Proposed Transfer:</span>
              <span className="font-semibold text-brand-700">
                {recommendation.recommended_transfer_quantity} units ({recommendation.source_location} → {recommendation.destination_location})
              </span>
            </div>
          </div>

          {/* Mandatory Reason Dropdown */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Override Reason <span className="text-rose-500">*</span>
            </label>
            <select
              value={reason}
              onChange={(e) => {
                setReason(e.target.value);
                setValidationError('');
              }}
              className="w-full text-sm rounded-lg border border-slate-300 px-3 py-2 bg-white text-slate-800 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              required
            >
              {OVERRIDE_REASONS.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {/* Staff Role */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Authorized Staff Role <span className="text-rose-500">*</span>
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full text-sm rounded-lg border border-slate-300 px-3 py-2 bg-white text-slate-800 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              required
            >
              {ROLES.map((ro) => (
                <option key={ro} value={ro}>
                  {ro}
                </option>
              ))}
            </select>
          </div>

          {/* Clinical Notes */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Clinical Context / Rationale Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. 15 units reserved for urgent scheduled pediatric infusion; cancel candidate shipment."
              rows={3}
              className="w-full text-sm rounded-lg border border-slate-300 px-3 py-2 text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-brand-500 focus:outline-none"
            />
          </div>

          {validationError && (
            <p className="text-xs text-rose-600 font-medium bg-rose-50 p-2.5 rounded-lg border border-rose-200">
              {validationError}
            </p>
          )}

          {/* Footer Controls */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-lg shadow-sm transition-colors focus:ring-2 focus:ring-amber-500"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Recording Override...</span>
                </>
              ) : (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Submit Override</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
