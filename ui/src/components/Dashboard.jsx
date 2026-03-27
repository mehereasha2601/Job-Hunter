import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading stats...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
        <button onClick={loadStats} className="mt-2 text-sm text-red-600 underline">
          Retry
        </button>
      </div>
    );
  }

  const topCompanies = Object.entries(stats.by_company)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 uppercase">Total Scraped</div>
          <div className="mt-2 text-3xl font-bold text-gray-900">{stats.total_scraped}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 uppercase">Scored</div>
          <div className="mt-2 text-3xl font-bold text-blue-600">{stats.total_scored}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 uppercase">Tailored</div>
          <div className="mt-2 text-3xl font-bold text-purple-600">{stats.total_tailored}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 uppercase">Applied</div>
          <div className="mt-2 text-3xl font-bold text-green-600">{stats.total_applied}</div>
        </div>
      </div>

      {/* By Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Jobs by Status</h2>
        <div className="space-y-2">
          {Object.entries(stats.by_status).map(([status, count]) => (
            <div key={status} className="flex items-center justify-between">
              <span className="text-sm text-gray-700 capitalize">{status}</span>
              <span className="text-sm font-medium text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* By Source */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Jobs by Source</h2>
        <div className="space-y-2">
          {Object.entries(stats.by_source).map(([source, count]) => (
            <div key={source} className="flex items-center justify-between">
              <span className="text-sm text-gray-700 capitalize">{source}</span>
              <span className="text-sm font-medium text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Companies */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Companies</h2>
        <div className="space-y-2">
          {topCompanies.map(([company, count]) => (
            <div key={company} className="flex items-center justify-between">
              <span className="text-sm text-gray-700">{company}</span>
              <span className="text-sm font-medium text-gray-900">{count} jobs</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
