import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Uploads / long-running semantic-index building can take longer.
const longClient = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export function setAuthToken(token) {
  const header = token ? `Bearer ${token}` : null
  for (const c of [client, longClient]) {
    if (header) {
      c.defaults.headers.common.Authorization = header
    } else {
      delete c.defaults.headers.common.Authorization
    }
  }
}

// If a token expires mid-session, force back to login rather than showing
// confusing partial/blank pages.
function handleAuthError(error) {
  if (error?.response?.status === 401) {
    localStorage.removeItem('rexplore-token')
    setAuthToken(null)
    if (!window.location.pathname.startsWith('/login')) {
      window.location.href = '/login'
    }
  }
  return Promise.reject(error)
}

client.interceptors.response.use((r) => r, handleAuthError)
longClient.interceptors.response.use((r) => r, handleAuthError)

export const api = {
  // Auth
  register: (fullName, email, password, confirmPassword) =>
    client.post('/auth/register', {
      full_name: fullName,
      email,
      password,
      confirm_password: confirmPassword,
    }),
  login: (email, password) => client.post('/auth/login', { email, password }),
  logout: () => client.post('/auth/logout'),
  me: () => client.get('/auth/me'),

  // Papers
  uploadPaper: (file, onProgress) => {
    const form = new FormData()
    form.append('file', file)
    return longClient.post('/papers/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt) => {
        if (onProgress && evt.total) onProgress(Math.round((evt.loaded * 100) / evt.total))
      },
    })
  },
  listPapers: () => client.get('/papers'),
  getPaper: (id) => client.get(`/papers/${id}`),
  // File endpoints require the auth header, so plain <a href> links can't
  // hit them directly - fetch as a blob and open/download that instead.
  openPaperFile: async (id) => {
    const res = await longClient.get(`/papers/${id}/file`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(res.data)
    window.open(url, '_blank', 'noopener')
    setTimeout(() => window.URL.revokeObjectURL(url), 60000)
  },
  comparePapers: (paperIds) => client.post('/papers/compare', { paper_ids: paperIds }),

  // Queries
  askQuestion: (paperId, question) => longClient.post('/queries', { paper_id: paperId, question }),
  getQueryHistory: (paperId) => client.get(`/queries/paper/${paperId}`),

  // Datasets
  getDatasetsForPaper: (paperId) => client.get(`/datasets/paper/${paperId}`),
  refreshDatasetSearch: (datasetId) => longClient.get(`/datasets/${datasetId}/search`),
  createSyntheticDataset: (datasetId, payload) => client.post(`/datasets/${datasetId}/synthetic`, payload),
  downloadSyntheticDataset: async (syntheticId) => {
    const res = await client.get(`/datasets/synthetic/${syntheticId}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(res.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `synthetic_dataset_${syntheticId}.csv`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => window.URL.revokeObjectURL(url), 60000)
  },

  // Analytics
  getAnalyticsOverview: () => client.get('/analytics/overview'),
  getAnalyticsFeatures: () => client.get('/analytics/features'),

  // Health
  health: () => client.get('/health'),
}

export default api
