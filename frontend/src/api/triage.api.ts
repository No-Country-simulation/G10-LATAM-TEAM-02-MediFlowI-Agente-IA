/**
 * MediFlow - API client wrapper sobre el cliente generado.
 * Este archivo es MANUAL. Wrappea _generated/api/ para agregar
 * lógica de negocio (headers, error handling, etc.)
 */

import type { ClinicalDocumentType } from '../constants/clinicalDocumentTypes'
import { apiRequest } from './httpClient'

export interface DocumentoClinicoPayload {
  documento_id: string
  tipo_archivo: 'PDF' | 'IMAGEN' | 'TEXTO' | 'JSON'
  documento_texto?: string
  documento_base64?: string
  canal_origen?: string
  metadata?: Record<string, unknown>
}

export interface ResultadoTriaje {
  status: 'procesado' | 'error' | 'pendiente_auditoria'
  documento_id: string
  clasificacion: {
    tipo_documento: ClinicalDocumentType
    especialidad?: string
    nivel_prioridad: 'Urgente' | 'Rutina' | 'Ambiguo'
    score_confianza_clasificacion: number
  }
  datos_extraidos: {
    paciente?: { nombre?: string; edad?: number; documento_identidad?: string; historia_clinica?: string }
    medico_solicitante?: { nombre?: string; matricula?: string }
    diagnostico_principal?: string
    cie10_sugerido?: string
    hallazgos_clave?: string[]
  }
  decision_enrutamiento: {
    destino_principal: 'Cola_Emergencia_Medica' | 'Cola_Rutina' | 'Cola_Auditoria_Humana' | 'Cola_Revision_Ambigua'
    requiere_auditoria_humana: boolean
    justificacion_enrutamiento: string
    notificacion_generada?: { canal: string; mensaje: string }
  }
  almacenamiento_oci?: {
    bucket: string
    ruta_objeto: string
    status_backup: 'exito' | 'error' | 'pendiente'
  }
  tiempo_procesamiento_ms?: number
  created_at?: string
}

/** Envía un documento al agente para triaje */
export async function procesarDocumento(
  payload: DocumentoClinicoPayload,
): Promise<ResultadoTriaje> {
  return apiRequest<ResultadoTriaje>('/triage', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/** Sube un archivo PDF/imagen para triaje */
export async function subirArchivo(
  documentoId: string,
  canalOrigen: string,
  archivo: File,
): Promise<ResultadoTriaje> {
  const form = new FormData()
  form.append('documento_id', documentoId)
  form.append('canal_origen', canalOrigen)
  form.append('archivo', archivo)

  return apiRequest<ResultadoTriaje>('/triage/upload', {
    method: 'POST',
    body: form,
  })
}

/** Lista documentos procesados */
export async function listarDocumentos(params?: {
  estado?: string
  nivel_prioridad?: string
  limit?: number
}): Promise<{ total: number; items: ResultadoTriaje[] }> {
  const qs = new URLSearchParams()
  if (params?.estado) qs.set('estado', params.estado)
  if (params?.nivel_prioridad) qs.set('nivel_prioridad', params.nivel_prioridad)
  if (params?.limit) qs.set('limit', String(params.limit))

  const query = qs.toString()
  return apiRequest<{ total: number; items: ResultadoTriaje[] }>(`/documents${query ? `?${query}` : ''}`)
}

/** Registra decisión de auditoría humana */
export async function registrarAuditoria(
  documentoId: string,
  decision: 'aprobar' | 'rechazar' | 'reclasificar',
  comentario?: string,
): Promise<ResultadoTriaje> {
  return apiRequest<ResultadoTriaje>(`/documents/${encodeURIComponent(documentoId)}`, {
    method: 'PATCH',
    body: JSON.stringify({ decision, comentario }),
  })
}

export interface ConfiguracionSistema {
  storage_mode: 'LOCAL' | 'OCI'
  oci_configured: boolean
  llm_provider: string
  llm_configured: boolean
  database_url_configured: boolean
}

/** Obtiene la configuración actual del sistema */
export async function obtenerConfiguracion(): Promise<ConfiguracionSistema> {
  return apiRequest<ConfiguracionSistema>('/settings')
}

/** Actualiza la configuración del sistema (ej. modo de almacenamiento) */
export async function actualizarConfiguracion(
  storageMode: 'LOCAL' | 'OCI',
): Promise<ConfiguracionSistema> {
  return apiRequest<ConfiguracionSistema>('/settings', {
    method: 'POST',
    body: JSON.stringify({ storage_mode: storageMode }),
  })
}

