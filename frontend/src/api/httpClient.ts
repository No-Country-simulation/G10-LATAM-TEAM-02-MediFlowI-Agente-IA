const configuredApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const API_BASE_URL = configuredApiUrl.replace(/\/+$/, '')

function getAccessToken(): string | null {
  const rawSession = localStorage.getItem('mediflow_auth_session')
  if (!rawSession) return null

  try {
    const session = JSON.parse(rawSession) as { access_token?: string }
    return session.access_token ?? null
  } catch {
    localStorage.removeItem('mediflow_auth_session')
    return null
  }
}

function extractErrorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') return fallback

  const body = payload as {
    mensaje?: string
    detail?: string | { mensaje?: string }
  }
  if (body.mensaje) return body.mensaje
  if (typeof body.detail === 'string') return body.detail
  return body.detail?.mensaje || fallback
}

export interface ApiRequestOptions extends RequestInit {
  auth?: boolean
  token?: string
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { auth = true, token: explicitToken, ...init } = options
  const token = explicitToken || (auth ? getAccessToken() : null)
  const headers = new Headers(init.headers)

  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  } catch {
    throw new Error('No se pudo conectar con el servidor de MediFlow.')
  }

  const payload = await response.json().catch(() => null)
  if (!response.ok && response.status !== 207) {
    throw new Error(extractErrorMessage(payload, `La solicitud falló (${response.status}).`))
  }

  return payload as T
}
