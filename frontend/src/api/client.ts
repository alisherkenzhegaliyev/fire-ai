import axios from 'axios'
import { useAppStore } from '../store/appStore'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 30000,
})

client.interceptors.request.use((config) => {
  const sessionId = useAppStore.getState().sessionId
  if (sessionId && config.params == null) {
    config.params = { session_id: sessionId }
  } else if (sessionId && config.params != null) {
    config.params.session_id = sessionId
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
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
