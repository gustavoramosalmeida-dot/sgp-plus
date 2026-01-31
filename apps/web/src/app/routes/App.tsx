/** Main app router */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../../core/auth/AuthContext'
import LoginPage from '../../features/auth/LoginPage'
import HomePage from '../../features/home/HomePage'
import { loadConfig } from '../../core/config/loadConfig'
import { useEffect, useState } from 'react'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <div>Carregando...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  const [configLoaded, setConfigLoaded] = useState(false)

  useEffect(() => {
    loadConfig().then(() => setConfigLoaded(true))
  }, [])

  if (!configLoaded) {
    return <div>Carregando configuração...</div>
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
