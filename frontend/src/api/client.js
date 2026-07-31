/**
 * Thin wrapper over the Flask API.
 *
 * Paths are relative, so in dev the Vite proxy (vite.config.js) forwards them
 * to :5000 and in production Flask serves both the SPA and the API.
 */

const BASE = '/api'

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, options)

  if (response.status === 204) return null

  const contentType = response.headers.get('content-type') || ''
  const body = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    throw new Error(body?.error || `Request failed (${response.status})`)
  }
  return body
}

function postJson(path, payload) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export const api = {
  listSubjects: () => request('/subjects'),
  createSubject: (name) => postJson('/subjects', { name }),
  deleteSubject: (id) => request(`/subjects/${id}`, { method: 'DELETE' }),

  listSessions: () => request('/sessions'),
  createSession: (payload) => postJson('/sessions', payload),
  deleteSession: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),

  summary: () => request('/analytics/summary'),

  // A plain <a download> hits this directly so the browser handles the save.
  exportUrl: `${BASE}/data/export`,
  importCsv: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/data/import', { method: 'POST', body: form })
  },
}
