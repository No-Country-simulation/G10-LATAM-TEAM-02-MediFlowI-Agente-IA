import { createContext } from 'react'
import type { User } from '../api/auth.api'

export type SessionUser = User & { token: string }
export interface LoginResult { success: boolean; user?: SessionUser; message?: string }
export interface AuthContextValue {
  user: SessionUser | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  login: (documentoIdentidad: string, password: string) => Promise<LoginResult>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
