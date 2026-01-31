/** HTTP client with credentials */

import { loadConfig } from '../config/loadConfig'

export interface ApiError {
  detail: string
}

async function getBaseUrl(): Promise<string> {
  const config = await loadConfig()
  return config.apiBaseUrl
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = await getBaseUrl()
  const url = `${baseUrl}${endpoint}`

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Always include cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (response.status === 401) {
    // Unauthorized - trigger logout
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: 'Unknown error',
    }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  if (response.status === 204 || (response.headers.get('content-length') === '0')) {
    return undefined as T
  }

  return response.json()
}
