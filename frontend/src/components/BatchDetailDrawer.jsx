import React from 'react';
import { X, Calendar, MapPin, AlertCircle, ShieldCheck, Thermometer, DollarSign, Activity } from 'lucide-react';

export default function BatchDetailDrawer({ batch, isOpen, onClose }) {
  if (!isOpen || !batch) return null;

  const isNearExpiry = batch.days_to_expiry <= 30 && batch.days_to_expiry > 0;
  const isExpired = batch.days_to_expiry <= 0;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white h-full shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-lg bg-brand-50 border border-brand-200 text-brand-600 flex items-center justify-center font-bold text-sm">
              {batch.medicine_code.slice(4)}
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-base">{batch.batch_id}</h3>
              <p className="text-xs text-slate-500">{batch.medicine_code} • {batch.medicine_category}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Medicine Title Card */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Clinical Formulation</span>
            <h4 className="text-sm font-semibold text-slate-900 mt-1">{batch.medicine_name}</h4>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg border border-slate-200 bg-white">
              <span className="text-[11px] font-medium text-slate-500">Current Stock</span>
              <div className="text-lg font-bold text-slate-900">{batch.quantity} units</div>
            </div>
            <div className="p-3 rounded-lg border border-slate-200 bg-white">
              <span className="text-[11px] font-medium text-slate-500">Total Stock Value</span>
              <div className="text-lg font-bold text-slate-900">${batch.stock_value?.toLocaleString()}</div>
            </div>
            <div className="p-3 rounded-lg border border-slate-200 bg-white">
              <span className="text-[11px] font-medium text-slate-500">Unit Cost</span>
              <div className="text-lg font-bold text-slate-900">${batch.unit_value?.toFixed(2)}</div>
            </div>
            <div className="p-3 rounded-lg border border-slate-200 bg-white">
              <span className="text-[11px] font-medium text-slate-500">Local Daily Demand</span>
              <div className="text-lg font-bold text-slate-900">{batch.avg_daily_demand || 'N/A'} /day</div>
            </div>
          </div>

          {/* Expiry Status */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Expiry Profile</span>
            <div className={`p-4 rounded-xl border flex items-center justify-between ${
              isExpired
                ? 'bg-rose-50 border-rose-200 text-rose-800'
                : isNearExpiry
                ? 'bg-amber-50 border-amber-200 text-amber-800'
                : 'bg-emerald-50 border-emerald-200 text-emerald-800'
            }`}>
              <div className="flex items-center space-x-3">
                <Calendar className="w-5 h-5" />
                <div>
                  <div className="text-xs font-semibold">Expires {batch.expiry_date}</div>
                  <div className="text-xs font-medium opacity-80">
                    {isExpired ? 'Expired' : `${batch.days_to_expiry} days remaining`}
                  </div>
                </div>
              </div>
              <span className="text-xs font-bold px-2 py-1 rounded bg-white/80 border border-current shadow-xs">
                {isExpired ? 'EXPIRED' : isNearExpiry ? 'NEAR EXPIRY' : 'STABLE'}
              </span>
            </div>
          </div>

          {/* Logistics & Cold Chain */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Logistics & Candidate Route</span>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Current Location:</span>
                <span className="font-semibold text-slate-800 flex items-center space-x-1">
                  <MapPin className="w-3.5 h-3.5 text-brand-600" />
                  <span>{batch.source_location}</span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Candidate Target:</span>
                <span className="font-semibold text-slate-800">{batch.destination_location || 'None'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Transfer Distance:</span>
                <span className="font-semibold text-slate-800">{batch.transfer_distance_km ? `${batch.transfer_distance_km} km` : 'N/A'}</span>
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-slate-200">
                <span className="text-slate-500">Storage Requirement:</span>
                <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-semibold ${
                  batch.temperature_sensitive ? 'bg-cyan-50 text-cyan-700 border border-cyan-200' : 'bg-slate-100 text-slate-600'
                }`}>
                  <Thermometer className="w-3 h-3" />
                  <span>{batch.temperature_sensitive ? 'Cold Chain (2°C - 8°C)' : 'Ambient Controlled'}</span>
                </span>
              </div>
            </div>
          </div>

          {/* Validation & Data Quality */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Clinical Data Integrity</span>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-brand-600" />
                <span className="text-xs text-slate-700">Quality Score:</span>
              </div>
              <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                {batch.data_quality_score}%
              </span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <button
            onClick={onClose}
            className="w-full py-2 px-4 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-semibold text-xs transition-colors"
          >
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
}
