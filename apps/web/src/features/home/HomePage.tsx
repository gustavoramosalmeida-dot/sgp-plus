/** Home page */

import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../core/auth/AuthContext'
import { loadConfig } from '../../core/config/loadConfig'
import { useEffect, useState } from 'react'
import './HomePage.css'

export default function HomePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [config, setConfig] = useState<{ env: string; showEnvBadge: boolean } | null>(null)

  useEffect(() => {
    loadConfig().then((cfg) => {
      setConfig(cfg)
    })
  }, [])

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  const showBadge = config && (config.env === 'HML' || config.showEnvBadge)

  return (
    <div className="home-container">
      {showBadge && (
        <div className="env-badge">
          {config?.env === 'HML' ? 'HML' : config?.env}
        </div>
      )}
      <div className="home-content">
        <h1>Bem-vindo ao SGP+</h1>
        <p>Logado como: <strong>{user?.email}</strong></p>
        <button onClick={handleLogout}>Sair</button>
      </div>
    </div>
  )
}
