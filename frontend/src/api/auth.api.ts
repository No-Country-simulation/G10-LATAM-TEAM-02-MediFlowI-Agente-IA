/**
 * MediFlow — API Client para Autenticación y Gestión de Usuarios (RF-01 al RF-05)
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ documento_identidad, password }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Credenciales inválidas')
  }

  return response.json()
}

export async function logoutUser(token: string): Promise<void> {
  await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  }).catch(() => {})
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Sesión no válida o expirada')
  }

  return response.json()
}

export async function fetchUsers(token: string): Promise<User[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/users`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al obtener usuarios')
  }

  return response.json()
}

export async function createNewUser(token: string, userData: Partial<User> & { password: string }): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/v1/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al registrar usuario')
  }

  return response.json()
}

export async function updateUserDetails(token: string, userId: string, userData: Partial<User> & { password?: string }): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al actualizar usuario')
  }

  return response.json()
}
