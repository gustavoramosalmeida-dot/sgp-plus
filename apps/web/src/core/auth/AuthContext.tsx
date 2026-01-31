/** Auth context */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as loginApi, logout as logoutApi, getMe, AuthResponse, User, Role, Permission } from './authApi'

interface AuthContextType {
  user: User | null
  roles: Role[]
  permissions: Permission[]
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check auth on mount
    checkAuth()
  }, [])

  async function checkAuth() {
    try {
      setLoading(true)
      const data: AuthResponse = await getMe()
      setUser(data.user)
      setRoles(data.roles)
      setPermissions(data.permissions)
    } catch (error) {
      setUser(null)
      setRoles([])
      setPermissions([])
    } finally {
      setLoading(false)
    }
  }

  async function login(email: string, password: string) {
    const data: AuthResponse = await loginApi({ email, password })
    setUser(data.user)
    setRoles(data.roles)
    setPermissions(data.permissions)
  }

  async function logout() {
    try {
      await logoutApi()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setRoles([])
      setPermissions([])
    }
  }

  return (
    <AuthContext.Provider value={{ user, roles, permissions, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
