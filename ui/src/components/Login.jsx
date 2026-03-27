import { useState } from 'react';
import { setPassword } from '../api';

export default function Login({ onLogin }) {
  const [password, setPasswordInput] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Test authentication with the actual API endpoint
      const response = await fetch('http://localhost:8000/api/health', {
        headers: {
          'Authorization': 'Basic ' + btoa('user:' + password)
        }
      });
      
      if (response.ok) {
        // Password works! Save it and login
        setPassword(password);
        onLogin();
      } else if (response.status === 401) {
        setError('Invalid password');
        setPasswordInput('');
      } else {
        // Other error (e.g., 500 from database)
        const data = await response.json();
        setError(data.detail || 'Server error. Check that Supabase is configured.');
      }
    } catch (err) {
      setError('Connection error. Make sure the API server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Job Hunter
            </h1>
            <p className="text-gray-600">
              Automated Job Application Pipeline
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label 
                htmlFor="password" 
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPasswordInput(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
                required
                autoFocus
              />
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Hint: Check your .env file for UI_PASSWORD</p>
          </div>
        </div>
      </div>
    </div>
  );
}
