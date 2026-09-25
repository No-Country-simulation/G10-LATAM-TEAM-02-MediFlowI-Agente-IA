import { useContext } from 'react'
import { AuthContext } from '../context/auth-context'

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  return context
}
