import axios from 'axios'
import { useAppStore } from '../store/appStore'

// ── snake_case → camelCase transformer ───────────────────────────────────────
function toCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase())
}

function keysToCamel(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(keysToCamel)
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
        toCamel(k),
        keysToCamel(v),
      ])
    )
  }
  return obj
}

// ── Axios instance ────────────────────────────────────────────────────────────
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
   // 5 min — NLP per ticket can be slow with 30+ entries
})

// Attach session_id to every request that doesn't already have it
client.interceptors.request.use((config) => {
  const sessionId = useAppStore.getState().sessionId
  if (sessionId) {
    config.params = { ...config.params, session_id: sessionId }
  }
  return config
})

// Auto-convert snake_case response keys to camelCase
client.interceptors.response.use(
  (response) => {
    response.data = keysToCamel(response.data)
    return response
  },
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message ??
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

export default client