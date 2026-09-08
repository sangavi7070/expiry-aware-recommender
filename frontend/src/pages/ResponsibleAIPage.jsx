import React from 'react';
import {
  HeartHandshake,
  ShieldCheck,
  UserCheck,
  Eye,
  AlertTriangle,
  FileCheck,
  Lock,
  Database
} from 'lucide-react';

export default function ResponsibleAIPage() {
  const principles = [
    {
      title: '1. Zero Private Patient Data',
      icon: Lock,
      color: 'blue',
      description:
        'The system operates exclusively on synthetic batch numbers, fictional medicine codes (e.g. MED-A01), and anonymized clinic identifiers. Absolutely no protected health information (PHI) or patient records are collected or processed.',
    },
    {
      title: '2. Transparent Rule-Based Scoring',
      icon: Eye,
      color: 'emerald',
      description:
        'Unlike unexplainable deep learning models, every recommendation is generated from an open, deterministic mathematical formula (35% Expiry + 25% Surplus + 25% Destination Demand + 10% Location + 5% Data Quality). Every point in the score is traceable to clinical facts.',
    },
    {
      title: '3. Mandatory Human Confirmation (Rule 10)',
      icon: UserCheck,
      color: 'purple',
      description:
        'The system assists authorized staff but NEVER autonomously dispatches medicine. High-impact inter-clinic redistributions strictly require pharmacist confirmation, explicit rejection, or documented override.',
    },
    {
      title: '4. Explicit Uncertainty & Degradation',
      icon: AlertTriangle,
      color: 'amber',
      description:
        'Uncertainty is never hidden. If candidate clinic demand data is missing or cold-chain transit poses elevated risks, confidence levels immediately degrade to WARNING or LOW CONFIDENCE with prominent visual indicators.',
    },
    {
      title: '5. Structured Override Governance',
      icon: ShieldCheck,
      color: 'rose',
      description:
        'Clinicians can override any recommendation, but must select a standardized clinical reason (e.g. "Stock already allocated", "Temperature concern") and role accountability, preventing unrecorded deviations.',
    },
    {
      title: '6. Immutable Audit Trail',
      icon: FileCheck,
      color: 'cyan',
      description:
        'Every single clinical interaction (approval, rejection, override, notes, timestamps) is permanently recorded to an SQLite audit log to satisfy hospital accreditation and clinical governance standards.',
    },
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto animate-in fade-in duration-150">
      {/* Page Header */}
      <div className="border-b border-slate-200 pb-5">
        <div className="flex items-center space-x-2">
          <HeartHandshake className="w-7 h-7 text-brand-600" />
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Responsible AI & Clinical Governance</h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          Ethical engineering principles, explainability standards, and human-in-the-loop safeguards built into ExpiryAware.
        </p>
      </div>

      {/* Core Mission Banner */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md border border-slate-800 space-y-2">
        <span className="text-[11px] font-bold uppercase tracking-wider text-brand-400">Clinical Purpose Statement</span>
        <h2 className="text-lg font-bold">Assisting Clinical Judgment — Not Replacing It</h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          ExpiryAware is an intelligent clinical decision support system designed to minimize specialty medicine expiry waste and ensure critical biologics reach patients in need. The system is engineered to prioritize patient safety, data integrity, and physician oversight over computational autonomy.
        </p>
      </div>

      {/* Principles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {principles.map((p, idx) => {
          const Icon = p.icon;
          return (
            <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2.5">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center">
                  <Icon className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-slate-900 text-sm">{p.title}</h3>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                {p.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Verification Notice */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-brand-600" />
          <span>All records generated deterministically for testing and validation. No live hospital PHI used.</span>
        </div>
        <span className="font-mono text-[11px] font-bold text-slate-500">Seed: 42</span>
      </div>
    </div>
  );
}
