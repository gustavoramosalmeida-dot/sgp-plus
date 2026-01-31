/** Runtime configuration loader */

export interface AppConfig {
  env: string
  apiBaseUrl: string
  showEnvBadge: boolean
}

let configCache: AppConfig | null = null

export async function loadConfig(): Promise<AppConfig> {
  if (configCache) {
    return configCache
  }

  try {
    const response = await fetch('/config.json', { cache: 'no-store' })
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.status}`)
    }
    const config = await response.json()
    configCache = config as AppConfig
    return configCache
  } catch (error) {
    console.error('Failed to load config.json:', error)
    // Fallback config
    const fallback: AppConfig = {
      env: 'DES',
      apiBaseUrl: 'http://localhost:8000',
      showEnvBadge: false,
    }
    console.warn('Using fallback config:', fallback)
    return fallback
  }
}
