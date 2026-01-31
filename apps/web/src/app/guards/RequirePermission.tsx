/** RBAC guard component (scaffold for future use) */

import { ReactNode } from 'react'
import { useAuth } from '../../core/auth/AuthContext'

interface RequirePermissionProps {
  permission: string
  children: ReactNode
  fallback?: ReactNode
}

export function RequirePermission({ permission, children, fallback = null }: RequirePermissionProps) {
  const { permissions } = useAuth()

  const hasPermission = permissions.some((p) => p.code === permission)

  if (!hasPermission) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
