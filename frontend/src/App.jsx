import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import InventoryPage from './pages/InventoryPage';
import RecommendationsPage from './pages/RecommendationsPage';
import EvaluationPage from './pages/EvaluationPage';
import AuditLogPage from './pages/AuditLogPage';
import DataQualityPage from './pages/DataQualityPage';
import ResponsibleAIPage from './pages/ResponsibleAIPage';
import ResetDemoModal from './components/ResetDemoModal';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeRole, setActiveRole] = useState('Pharmacist');
  const [isResetModalOpen, setIsResetModalOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleResetConfirm = async () => {
    setIsResetting(true);
    try {
      await api.resetDemoData();
      setIsResetModalOpen(false);
      // Trigger re-render of current view with pristine seed
      setRefreshKey((k) => k + 1);
    } catch (err) {
      alert(`Reset failed: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      {/* Top Navigation */}
      <Navbar
        onResetDemoClick={() => setIsResetModalOpen(true)}
        activeRole={activeRole}
        setActiveRole={setActiveRole}
      />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex">
        {/* Desktop Sidebar Navigation */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Content View Container */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          {/* Mobile Tab Bar */}
          <div className="md:hidden flex overflow-x-auto space-x-2 pb-3 mb-4 border-b border-slate-200">
            {[
              { id: 'dashboard', label: 'Dashboard' },
              { id: 'inventory', label: 'Inventory' },
              { id: 'recommendations', label: 'Recommendations' },
              { id: 'evaluation', label: 'Evaluation' },
              { id: 'audit', label: 'Audit' },
              { id: 'data-quality', label: 'Quality' },
              { id: 'responsible-ai', label: 'Ethics' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'bg-brand-600 text-white'
                    : 'bg-white text-slate-600 border border-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Active Page View */}
          <div key={refreshKey}>
            {activeTab === 'dashboard' && <DashboardPage setActiveTab={setActiveTab} />}
            {activeTab === 'inventory' && <InventoryPage />}
            {activeTab === 'recommendations' && <RecommendationsPage activeRole={activeRole} />}
            {activeTab === 'evaluation' && <EvaluationPage />}
            {activeTab === 'audit' && <AuditLogPage />}
            {activeTab === 'data-quality' && <DataQualityPage />}
            {activeTab === 'responsible-ai' && <ResponsibleAIPage />}
          </div>
        </main>
      </div>

      {/* Confirmation Modal for Demo Data Reset */}
      <ResetDemoModal
        isOpen={isResetModalOpen}
        onClose={() => setIsResetModalOpen(false)}
        onConfirm={handleResetConfirm}
        isResetting={isResetting}
      />
    </div>
  );
}
