/** Auth API calls */

import { apiRequest } from '../http/client'

export interface LoginRequest {
  email: string
  password: string
}

export interface User {
  id: string
  email: string
  is_active: boolean
  created_at: string
}

export interface Role {
  id: string
  code: string
  name: string
}

export interface Permission {
  id: string
  code: string
  name: string
}

export interface AuthResponse {
  user: User
  roles: Role[]
  permissions: Permission[]
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function logout(): Promise<void> {
  await apiRequest('/auth/logout', {
    method: 'POST',
  })
}

export async function getMe(): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/auth/me')
}
