import { useState, useEffect } from 'react';
import { api } from '../api';

export default function JobTable() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [filters, setFilters] = useState({
    status: '',
    min_score: '',
    company: '',
    sort_by: 'score'  // NEW - default sort by score
  });
  const [tailoring, setTailoring] = useState(false);
  const [tailorSuccess, setTailorSuccess] = useState(false);

  useEffect(() => {
    loadJobs();
  }, [filters]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const cleanFilters = {};
      if (filters.status) cleanFilters.status = filters.status;
      if (filters.min_score) cleanFilters.min_score = parseFloat(filters.min_score);
      if (filters.company) cleanFilters.company = filters.company;
      if (filters.sort_by) cleanFilters.sort_by = filters.sort_by;  // NEW
      
      const data = await api.getJobs(cleanFilters);
      setJobs(data.jobs);
    } catch (err) {
      setError(err.message || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectJob = (jobId) => {
    setSelectedJobs(prev =>
      prev.includes(jobId)
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    );
  };

  const handleSelectAll = () => {
    if (selectedJobs.length === jobs.length) {
      setSelectedJobs([]);
    } else {
      setSelectedJobs(jobs.map(j => j.id));
    }
  };

  const handleStatusChange = async (jobId, newStatus) => {
    try {
      await api.updateJobStatus(jobId, newStatus);
      // Update local state
      setJobs(prev => prev.map(job =>
        job.id === jobId ? { ...job, status: newStatus } : job
      ));
    } catch (err) {
      alert(`Failed to update status: ${err.message}`);
    }
  };

  const handleTailorSelected = async () => {
    if (selectedJobs.length === 0) {
      alert('Please select at least one job');
      return;
    }

    if (selectedJobs.length > 10) {
      alert('Maximum 10 jobs per batch');
      return;
    }

    if (!confirm(`Tailor ${selectedJobs.length} job(s)?`)) {
      return;
    }

    try {
      setTailoring(true);
      const result = await api.tailorJobs(selectedJobs);
      setTailorSuccess(true);
      alert(`Success! ${result.message}\n\nCheck GitHub Actions for progress.`);
      setSelectedJobs([]);
      setTimeout(() => setTailorSuccess(false), 5000);
    } catch (err) {
      alert(`Failed to trigger tailoring: ${err.message}`);
    } finally {
      setTailoring(false);
    }
  };

  const getScoreBadgeClass = (score) => {
    if (score >= 8) return 'score-badge score-high';
    if (score >= 6) return 'score-badge score-medium';
    return 'score-badge score-low';
  };

  const getStatusBadgeClass = (status) => {
    return `status-badge status-${status}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffHours = diffMs / 1000 / 60 / 60;
      const diffDays = diffHours / 24;
      
      if (diffHours < 1) return 'Just now';
      if (diffHours < 24) return `${Math.floor(diffHours)}h ago`;
      if (diffDays < 7) return `${Math.floor(diffDays)}d ago`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
      
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return 'N/A';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading jobs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
        <button
          onClick={loadJobs}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All</option>
              <option value="seen">Seen</option>
              <option value="scored">Scored</option>
              <option value="tailored">Tailored</option>
              <option value="applied">Applied</option>
              <option value="interview">Interview</option>
              <option value="offer">Offer</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Score
            </label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.5"
              value={filters.min_score}
              onChange={(e) => setFilters(prev => ({ ...prev, min_score: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              placeholder="0-10"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company
            </label>
            <input
              type="text"
              value={filters.company}
              onChange={(e) => setFilters(prev => ({ ...prev, company: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              placeholder="Search..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
            <select
              value={filters.sort_by}
              onChange={(e) => setFilters(prev => ({ ...prev, sort_by: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="score">Score (Best Match)</option>
              <option value="date_posted">Date Posted (Newest)</option>
              <option value="first_seen_at">Recently Added</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ status: '', min_score: '', company: '', sort_by: 'score' })}
              className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      {selectedJobs.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center justify-between">
          <span className="text-sm font-medium text-blue-900">
            {selectedJobs.length} job(s) selected
          </span>
          <button
            onClick={handleTailorSelected}
            disabled={tailoring}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {tailoring ? 'Triggering...' : '🚀 Tailor Selected'}
          </button>
        </div>
      )}

      {tailorSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-700">
            ✅ Tailoring triggered successfully! Check GitHub Actions for progress.
          </p>
        </div>
      )}

      {/* Jobs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">
                <input
                  type="checkbox"
                  checked={jobs.length > 0 && selectedJobs.length === jobs.length}
                  onChange={handleSelectAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Posted
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                  No jobs found. Try adjusting your filters.
                </td>
              </tr>
            ) : (
              jobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      checked={selectedJobs.includes(job.id)}
                      onChange={() => handleSelectJob(job.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getScoreBadgeClass(job.score)}>
                      {job.score ? job.score.toFixed(1) : 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{job.company}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{job.title}</div>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:text-blue-800"
                    >
                      View posting →
                    </a>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(job.date_posted)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={job.status}
                      onChange={(e) => handleStatusChange(job.id, e.target.value)}
                      className={`${getStatusBadgeClass(job.status)} border-none text-xs font-medium cursor-pointer`}
                    >
                      <option value="seen">Seen</option>
                      <option value="scored">Scored</option>
                      <option value="tailored">Tailored</option>
                      <option value="applied">Applied</option>
                      <option value="response">Response</option>
                      <option value="interview">Interview</option>
                      <option value="offer">Offer</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {job.h1b_flag === 'confirmed' && (
                      <span className="text-green-600" title="H1B Sponsor">✓ H1B</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="text-sm text-gray-500 text-center">
        Showing {jobs.length} job{jobs.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}
