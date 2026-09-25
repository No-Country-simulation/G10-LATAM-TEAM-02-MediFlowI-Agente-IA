/**
 * MediFlow - API Client para Autenticación y Gestión de Usuarios (RF-01 al RF-05)
 */

import { apiRequest } from './httpClient'

export interface User {
  id: string
  documento_identidad: string
  nombres: string
  apellidos: string
  correo?: string
  telefono?: string
  rol: 'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'
  estado: 'ACTIVO' | 'INACTIVO'
  created_at?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
  mensaje: string
}

export async function loginUser(documento_identidad: string, password: string): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/auth/login', {
    method: 'POST',
    auth: false,
    body: JSON.stringify({ documento_identidad, password }),
  })
}

export async function logoutUser(token: string): Promise<void> {
  try {
    await apiRequest<unknown>('/auth/logout', { method: 'POST', token })
  } catch {
    // El cierre local de sesión debe continuar aunque el servidor no responda.
  }
}

export async function getCurrentUser(token: string): Promise<User> {
  return apiRequest<User>('/auth/me', { token })
}

export async function fetchUsers(token: string): Promise<User[]> {
  return apiRequest<User[]>('/users', { token })
}

export async function createNewUser(token: string, userData: Partial<User> & { password: string }): Promise<User> {
  return apiRequest<User>('/users', {
    method: 'POST',
    token,
    body: JSON.stringify(userData),
  })
}

export async function updateUserDetails(token: string, userId: string, userData: Partial<User> & { password?: string }): Promise<User> {
  return apiRequest<User>(`/users/${encodeURIComponent(userId)}`, {
    method: 'PUT',
    token,
    body: JSON.stringify(userData),
  })
}
