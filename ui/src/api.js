import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with auth
const createAuthClient = (password) => {
  return axios.create({
    baseURL: API_URL,
    auth: {
      username: 'user',
      password: password
    },
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

let apiClient = null;

export const setPassword = (password) => {
  apiClient = createAuthClient(password);
  localStorage.setItem('api_password', password);
};

export const getStoredPassword = () => {
  return localStorage.getItem('api_password');
};

export const clearPassword = () => {
  localStorage.removeItem('api_password');
  apiClient = null;
};

export const isAuthenticated = () => {
  return !!getStoredPassword();
};

// Initialize client if password exists
const storedPassword = getStoredPassword();
if (storedPassword) {
  apiClient = createAuthClient(storedPassword);
}

// API methods
export const api = {
  // Health check
  health: async () => {
    const response = await axios.get(`${API_URL}/api/health`);
    return response.data;
  },

  // Get all jobs with filters
  getJobs: async (filters = {}) => {
    if (!apiClient) throw new Error('Not authenticated');
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.min_score) params.append('min_score', filters.min_score);
    if (filters.company) params.append('company', filters.company);
    if (filters.source) params.append('source', filters.source);
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);
    
    const response = await apiClient.get(`/api/jobs?${params.toString()}`);
    return response.data;
  },

  // Get single job
  getJob: async (jobId) => {
    if (!apiClient) throw new Error('Not authenticated');
    const response = await apiClient.get(`/api/jobs/${jobId}`);
    return response.data;
  },

  // Update job status
  updateJobStatus: async (jobId, status) => {
    if (!apiClient) throw new Error('Not authenticated');
    const response = await apiClient.patch(`/api/jobs/${jobId}/status`, { status });
    return response.data;
  },

  // Get dashboard stats
  getStats: async () => {
    if (!apiClient) throw new Error('Not authenticated');
    const response = await apiClient.get('/api/stats');
    return response.data;
  },

  // Trigger tailoring
  tailorJobs: async (jobIds) => {
    if (!apiClient) throw new Error('Not authenticated');
    const response = await apiClient.post('/api/tailor', { job_ids: jobIds });
    return response.data;
  },

  // Get outputs
  getOutputs: async () => {
    if (!apiClient) throw new Error('Not authenticated');
    const response = await apiClient.get('/api/outputs');
    return response.data;
  }
};
