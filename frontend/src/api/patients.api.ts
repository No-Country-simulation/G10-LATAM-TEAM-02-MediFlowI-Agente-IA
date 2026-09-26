/**
 * MediFlow — API Client para Gestión de Pacientes (Módulo 2: RF-06 al RF-09)
 */

import { apiRequest } from './httpClient'

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

export async function fetchPatients(search?: string, token?: string): Promise<{ total: number; items: Paciente[] }> {
  const query = search ? `?search=${encodeURIComponent(search)}` : ''
  return apiRequest<{ total: number; items: Paciente[] }>(`/patients${query}`, { token })
}

export async function createPatient(payload: PacienteCreatePayload, token?: string): Promise<{ message: string; paciente: Paciente }> {
  return apiRequest<{ message: string; paciente: Paciente }>('/patients', {
    method: 'POST',
    token,
    body: JSON.stringify(payload),
  })
}

export async function updatePatient(id: string, payload: PacienteUpdatePayload, token?: string): Promise<{ message: string; paciente: Paciente }> {
  return apiRequest<{ message: string; paciente: Paciente }>(`/patients/${encodeURIComponent(id)}`, {
    method: 'PUT',
    token,
    body: JSON.stringify(payload),
  })
}

export async function fetchPatientDocuments(id: string, token?: string): Promise<HistorialDocumentosPacienteResponse> {
  return apiRequest<HistorialDocumentosPacienteResponse>(`/patients/${encodeURIComponent(id)}/documents`, { token })
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
  return apiRequest<{ total: number; items: DocumentoDisponible[] }>('/patients/unlinked-documents', { token })
}

export async function associateDocumentToPatient(patientId: string, documentoId: string, token?: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(
    `/patients/${encodeURIComponent(patientId)}/documents/${encodeURIComponent(documentoId)}/associate`,
    {
    method: 'POST',
      token,
    },
  )
}
