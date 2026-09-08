/**
 * Centralized API Service for ExpiryAware backend.
 * Handles network requests, error abstraction, and fallback state.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      let errorMsg = `Server responded with ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson.detail) {
          errorMsg = errorJson.detail;
        }
      } catch {
        // fallback to status text
      }
      const err = new Error(errorMsg);
      err.status = res.status;
      throw err;
    }
    return await res.json();
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error(
        'Unable to connect to the ExpiryAware backend server. Please verify that the backend is running on port 8000.'
      );
    }
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request('/api/health'),

  // Demo Reset
  resetDemoData: () => request('/api/seed', { method: 'POST' }),

  // Dashboard
  getDashboard: () => request('/api/dashboard'),

  // Inventory
  getInventory: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.location && params.location !== 'All') searchParams.append('location', params.location);
    if (params.category && params.category !== 'All') searchParams.append('category', params.category);
    if (params.search) searchParams.append('search', params.search);
    if (params.nearExpiryOnly) searchParams.append('near_expiry_only', 'true');
    if (params.tempSensitive !== undefined && params.tempSensitive !== null) {
      searchParams.append('temp_sensitive', params.tempSensitive);
    }
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request(`/api/inventory${query}`);
  },

  getInventoryBatch: (batchId) => request(`/api/inventory/${encodeURIComponent(batchId)}`),

  // Recommendations
  getRecommendations: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.priority && params.priority !== 'All') searchParams.append('priority', params.priority);
    if (params.status && params.status !== 'All') searchParams.append('status_filter', params.status);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request(`/api/recommendations${query}`);
  },

  getRecommendation: (recId) => request(`/api/recommendations/${encodeURIComponent(recId)}`),

  // Human Confirmation Actions
  approveRecommendation: (recId, data = {}) =>
    request(`/api/recommendations/${encodeURIComponent(recId)}/approve`, {
      method: 'POST',
      body: JSON.stringify({
        user_role: data.userRole || 'Pharmacist',
        reason: data.reason || 'Clinical confirmation verified.',
        notes: data.notes || '',
      }),
    }),

  rejectRecommendation: (recId, data = {}) =>
    request(`/api/recommendations/${encodeURIComponent(recId)}/reject`, {
      method: 'POST',
      body: JSON.stringify({
        user_role: data.userRole || 'Pharmacist',
        reason: data.reason || 'Clinical rejection.',
        notes: data.notes || '',
      }),
    }),

  overrideRecommendation: (recId, data) =>
    request(`/api/recommendations/${encodeURIComponent(recId)}/override`, {
      method: 'POST',
      body: JSON.stringify({
        user_role: data.userRole,
        reason: data.reason,
        notes: data.notes || '',
      }),
    }),

  // Audit Log
  getAuditLog: (action = null) => {
    const query = action && action !== 'All' ? `?action=${encodeURIComponent(action)}` : '';
    return request(`/api/audit${query}`);
  },

  // Data Quality
  getDataQuality: () => request('/api/data-quality'),

  // Evaluation
  getEvaluation: () => request('/api/evaluation'),
};
