import React, { useState, useEffect, useMemo } from 'react';
import {
  Search,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Eye,
  Thermometer,
  Calendar,
  AlertCircle,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import BatchDetailDrawer from '../components/BatchDetailDrawer';

export default function InventoryPage() {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [nearExpiryOnly, setNearExpiryOnly] = useState(false);
  const [tempSensitiveFilter, setTempSensitiveFilter] = useState('All');

  // Sorting state
  const [sortField, setSortField] = useState('days_to_expiry');
  const [sortDirection, setSortDirection] = useState('asc');

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);

  // Drawer state
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const fetchInventory = () => {
    setLoading(true);
    api.getInventory({
      location: selectedLocation,
      category: selectedCategory,
      search: searchTerm,
      nearExpiryOnly,
      tempSensitive: tempSensitiveFilter === 'All' ? null : tempSensitiveFilter === 'ColdChain',
    })
      .then((data) => {
        setBatches(data);
        setError(null);
        setCurrentPage(1);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchInventory();
  }, [selectedLocation, selectedCategory, nearExpiryOnly, tempSensitiveFilter]);

  // Client-side search & sorting
  const filteredAndSortedBatches = useMemo(() => {
    let result = [...batches];

    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      result = result.filter(
        (b) =>
          b.batch_id.toLowerCase().includes(q) ||
          b.medicine_code.toLowerCase().includes(q) ||
          b.medicine_name.toLowerCase().includes(q) ||
          b.source_location.toLowerCase().includes(q)
      );
    }

    result.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [batches, searchTerm, sortField, sortDirection]);

  // Pagination slice
  const paginatedBatches = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSortedBatches.slice(start, start + pageSize);
  }, [filteredAndSortedBatches, currentPage, pageSize]);

  const totalPages = Math.ceil(filteredAndSortedBatches.length / pageSize) || 1;

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleRowClick = (batch) => {
    setSelectedBatch(batch);
    setIsDrawerOpen(true);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Medicine Stock Inventory</h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse and inspect active medicine batches across all regional clinic dispensaries.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            {filteredAndSortedBatches.length} Batches Found
          </span>
        </div>
      </div>

      {/* Filter Controls Bar */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search batch, medicine..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full text-xs rounded-lg border border-slate-300 pl-9 pr-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
            />
          </div>

          {/* Location */}
          <div>
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="w-full text-xs rounded-lg border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
            >
              <option value="All">All Locations</option>
              <option value="Clinic-A">Clinic-A</option>
              <option value="Clinic-B">Clinic-B</option>
              <option value="Clinic-C">Clinic-C</option>
              <option value="Clinic-D">Clinic-D</option>
              <option value="Clinic-E">Clinic-E</option>
            </select>
          </div>

          {/* Category */}
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full text-xs rounded-lg border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
            >
              <option value="All">All Categories</option>
              <option value="Oncology">Oncology</option>
              <option value="Endocrine">Endocrine</option>
              <option value="Immunology">Immunology</option>
              <option value="Critical Anti-Infective">Critical Anti-Infective</option>
              <option value="Hematology">Hematology</option>
            </select>
          </div>

          {/* Cold Chain Filter */}
          <div>
            <select
              value={tempSensitiveFilter}
              onChange={(e) => setTempSensitiveFilter(e.target.value)}
              className="w-full text-xs rounded-lg border border-slate-300 px-3 py-2 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
            >
              <option value="All">All Storage Types</option>
              <option value="ColdChain">Cold Chain (2-8°C)</option>
              <option value="Ambient">Standard Ambient</option>
            </select>
          </div>

          {/* Near Expiry Toggle */}
          <div className="flex items-center">
            <label className="flex items-center space-x-2 text-xs font-semibold text-slate-700 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={nearExpiryOnly}
                onChange={(e) => setNearExpiryOnly(e.target.checked)}
                className="rounded border-slate-300 text-brand-600 focus:ring-brand-500 w-4 h-4 cursor-pointer"
              />
              <span className="text-rose-700 bg-rose-50 px-2 py-1 rounded border border-rose-200">
                Near Expiry Only (≤30d)
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Inventory Table Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-12 space-y-3">
            <RefreshCw className="w-6 h-6 text-brand-600 animate-spin" />
            <p className="text-xs text-slate-500 font-medium">Loading inventory records...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-xs">{error}</div>
        ) : filteredAndSortedBatches.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-2">
            <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
            <p className="text-sm font-semibold text-slate-700">No batches match the selected filters.</p>
            <p className="text-xs text-slate-400">Try adjusting your search criteria or resetting filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
                  <th className="p-3.5 cursor-pointer" onClick={() => handleSort('batch_id')}>
                    <div className="flex items-center space-x-1">
                      <span>Batch</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5 cursor-pointer" onClick={() => handleSort('medicine_code')}>
                    <div className="flex items-center space-x-1">
                      <span>Medicine</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5 cursor-pointer" onClick={() => handleSort('source_location')}>
                    <div className="flex items-center space-x-1">
                      <span>Location</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5 text-right cursor-pointer" onClick={() => handleSort('quantity')}>
                    <div className="flex items-center justify-end space-x-1">
                      <span>Qty</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5 cursor-pointer" onClick={() => handleSort('expiry_date')}>
                    <div className="flex items-center space-x-1">
                      <span>Expiry Date</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5 text-right cursor-pointer" onClick={() => handleSort('days_to_expiry')}>
                    <div className="flex items-center justify-end space-x-1">
                      <span>Days Left</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5 text-right">Local Demand</th>
                  <th className="p-3.5 text-right cursor-pointer" onClick={() => handleSort('stock_value')}>
                    <div className="flex items-center justify-end space-x-1">
                      <span>Stock Value</span>
                      <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="p-3.5">Storage</th>
                  <th className="p-3.5 text-center">Integrity</th>
                  <th className="p-3.5 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {paginatedBatches.map((batch) => {
                  const isNear = batch.days_to_expiry <= 30 && batch.days_to_expiry > 0;
                  const isExpired = batch.days_to_expiry <= 0;
                  return (
                    <tr
                      key={batch.batch_id}
                      onClick={() => handleRowClick(batch)}
                      className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                    >
                      <td className="p-3.5 font-bold text-slate-900">{batch.batch_id}</td>
                      <td className="p-3.5">
                        <div className="font-semibold text-slate-800">{batch.medicine_code}</div>
                        <div className="text-[11px] text-slate-500 truncate max-w-[200px]" title={batch.medicine_name}>
                          {batch.medicine_name}
                        </div>
                      </td>
                      <td className="p-3.5 font-medium text-slate-700">{batch.source_location}</td>
                      <td className="p-3.5 text-right font-bold text-slate-900">{batch.quantity}</td>
                      <td className="p-3.5 text-slate-600 font-mono text-[11px]">{batch.expiry_date}</td>
                      <td className="p-3.5 text-right">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                            isExpired
                              ? 'bg-rose-100 text-rose-800 border border-rose-200'
                              : isNear
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {isExpired ? 'Expired' : `${batch.days_to_expiry}d`}
                        </span>
                      </td>
                      <td className="p-3.5 text-right text-slate-600">
                        {batch.avg_daily_demand ? `${batch.avg_daily_demand}/d` : 'N/A'}
                      </td>
                      <td className="p-3.5 text-right font-bold text-slate-900 font-mono">
                        ${batch.stock_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="p-3.5">
                        {batch.temperature_sensitive ? (
                          <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-cyan-700 bg-cyan-50 px-2 py-0.5 rounded border border-cyan-200">
                            <Thermometer className="w-2.5 h-2.5" />
                            <span>Cold Chain</span>
                          </span>
                        ) : (
                          <span className="text-[10px] text-slate-500">Ambient</span>
                        )}
                      </td>
                      <td className="p-3.5 text-center">
                        <span
                          className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            batch.validation_status === 'VALID'
                              ? 'bg-emerald-50 text-emerald-700'
                              : batch.validation_status === 'WARNING'
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-rose-50 text-rose-700'
                          }`}
                        >
                          {batch.validation_status}
                        </span>
                      </td>
                      <td className="p-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => handleRowClick(batch)}
                          className="p-1.5 text-slate-400 hover:text-brand-600 rounded hover:bg-slate-100 transition-colors"
                          title="View batch details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
          <div>
            Showing{' '}
            <span className="font-semibold text-slate-900">
              {filteredAndSortedBatches.length > 0 ? (currentPage - 1) * pageSize + 1 : 0}
            </span>{' '}
            to{' '}
            <span className="font-semibold text-slate-900">
              {Math.min(currentPage * pageSize, filteredAndSortedBatches.length)}
            </span>{' '}
            of <span className="font-semibold text-slate-900">{filteredAndSortedBatches.length}</span> batches
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="text-xs rounded border border-slate-300 py-1 px-2 bg-white focus:outline-none"
            >
              <option value={10}>10 per page</option>
              <option value={15}>15 per page</option>
              <option value={25}>25 per page</option>
              <option value={50}>50 per page</option>
            </select>

            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded border border-slate-300 bg-white text-slate-600 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-semibold text-slate-800">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded border border-slate-300 bg-white text-slate-600 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Detail Drawer */}
      <BatchDetailDrawer
        batch={selectedBatch}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  );
}
