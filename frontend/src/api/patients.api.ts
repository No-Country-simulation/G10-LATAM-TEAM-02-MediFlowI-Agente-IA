/**
 * MediFlow — API Client para Gestión de Pacientes (Módulo 2: RF-06 al RF-09)
 */

const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  let clean = envUrl.trim().replace(/\/+$/, '')
  if (!clean.endsWith('/api/v1')) {
    clean = `${clean}/api/v1`
  }
  return clean
}

const API_BASE_URL = getApiBaseUrl()

export interface Paciente {
  id: string
  tipo_documento: 'DNI' | 'CE' | 'PASAPORTE'
  numero_documento: string
  historia_clinica?: string
  nombres: string
  apellidos: string
  nombre_completo: string
  fecha_nacimiento?: string
  sexo?: 'M' | 'F' | 'OTRO' | null
  telefono?: string
  correo?: string
  created_at?: string
}

export interface PacienteCreatePayload {
  tipo_documento: 'DNI' | 'CE' | 'PASAPORTE'
  numero_documento: string
  historia_clinica?: string
  nombres: string
  apellidos: string
  fecha_nacimiento?: string
  sexo?: 'M' | 'F' | 'OTRO' | null
  telefono?: string
  correo?: string
}

export interface PacienteUpdatePayload {
  tipo_documento?: 'DNI' | 'CE' | 'PASAPORTE'
  numero_documento?: string
  historia_clinica?: string
  nombres?: string
  apellidos?: string
  fecha_nacimiento?: string
  sexo?: 'M' | 'F' | 'OTRO' | null
  telefono?: string
  correo?: string
}

export interface DocumentoPaciente {
  id: string
  documento_id: string
  tipo_archivo: string
  canal_origen: string
  status: string
  tipo_documento?: string
  especialidad?: string
  nivel_prioridad?: string
  score_confianza?: number
  datos_extraidos_ia?: {
    nombre_detectado?: string
    edad_detectada?: number
    dni_hc_detectado?: string
    medico_nombre?: string
    diagnostico?: string
    cie10?: string
  }
  destino_principal?: string
  created_at?: string
}

export interface HistorialDocumentosPacienteResponse {
  paciente_id: string
  nombre_completo: string
  numero_documento: string
  historia_clinica?: string
  total_documentos: number
  documentos: DocumentoPaciente[]
}

const getHeaders = (token?: string) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

export async function fetchPatients(search?: string, token?: string): Promise<{ total: number; items: Paciente[] }> {
  const url = new URL(`${API_BASE_URL}/patients`)
  if (search) {
    url.searchParams.append('search', search)
  }

  const response = await fetch(url.toString(), {
    headers: getHeaders(token),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al obtener listado de pacientes')
  }

  return response.json()
}

export async function createPatient(payload: PacienteCreatePayload, token?: string): Promise<{ message: string; paciente: Paciente }> {
  const response = await fetch(`${API_BASE_URL}/patients`, {
    method: 'POST',
    headers: getHeaders(token),
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al registrar paciente')
  }

  return response.json()
}

export async function updatePatient(id: string, payload: PacienteUpdatePayload, token?: string): Promise<{ message: string; paciente: Paciente }> {
  const response = await fetch(`${API_BASE_URL}/patients/${id}`, {
    method: 'PUT',
    headers: getHeaders(token),
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al actualizar paciente')
  }

  return response.json()
}

export async function fetchPatientDocuments(id: string, token?: string): Promise<HistorialDocumentosPacienteResponse> {
  const response = await fetch(`${API_BASE_URL}/patients/${id}/documents`, {
    headers: getHeaders(token),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al obtener historial de documentos del paciente')
  }

  return response.json()
}

export interface DocumentoDisponible {
  id: string
  documento_id: string
  tipo_documento: string
  tipo_archivo: string
  paciente_nombre?: string
  created_at?: string
}

export async function fetchUnlinkedDocuments(token?: string): Promise<{ total: number; items: DocumentoDisponible[] }> {
  const response = await fetch(`${API_BASE_URL}/patients/unlinked-documents`, {
    headers: getHeaders(token),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al obtener documentos disponibles')
  }

  return response.json()
}

export async function associateDocumentToPatient(patientId: string, documentoId: string, token?: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE_URL}/patients/${patientId}/documents/${documentoId}/associate`, {
    method: 'POST',
    headers: getHeaders(token),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al asociar documento al paciente')
  }

  return response.json()
}
