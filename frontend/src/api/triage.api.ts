/**
 * MediFlow - API client wrapper sobre el cliente generado.
 * Este archivo es MANUAL. Wrappea _generated/api/ para agregar
 * lógica de negocio (headers, error handling, etc.)
 */

import type { DocumentoClinico, ResultadoTriaje, ConfiguracionSistema } from '../_generated/api'
import { apiRequest } from './httpClient'

export type { ResultadoTriaje, ConfiguracionSistema } from '../_generated/api'
export type DocumentoClinicoPayload = DocumentoClinico

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

