import type { ClinicalDocument } from '../types/documents'
import type { ResultadoTriaje } from './triage.api'
import { apiRequest } from './httpClient'
import { normalizeBackendDocument } from './documentsApi'

interface AuditCorrection {
  paciente?: { nombre?: string; dni?: string; edad?: string | number }
  medico?: { nombre?: string; cmp?: string }
  diagnostico?: string
  cie10?: string
  tipo_documento?: string
  especialidad?: string
  prioridad?: string
  destino?: string
}

interface AuditPayload {
  decision: 'aprobar' | 'rechazar' | 'reclasificar'
  comentario?: string
  nueva_clasificacion?: Record<string, unknown>
  datos_corregidos?: AuditCorrection
}

function toBackendPriority(priority?: string): 'Urgente' | 'Rutina' | 'Ambiguo' | undefined {
  if (!priority) return undefined
  if (priority.toUpperCase() === 'URGENTE') return 'Urgente'
  if (priority.toUpperCase() === 'PRIORITARIO') return 'Ambiguo'
  return 'Rutina'
}

function toBackendDestination(destination?: string): string | undefined {
  if (!destination) return undefined
  const normalized = destination.trim().toUpperCase().replace(/\s+/g, '_')
  if (normalized.includes('EMERGENCIA')) return 'Cola_Emergencia_Medica'
  if (normalized.includes('AUDITOR')) return 'Cola_Auditoria_Humana'
  if (normalized.includes('AMBIGU')) return 'Cola_Revision_Ambigua'
  return normalized.startsWith('COLA_') ? destination : 'Cola_Rutina'
}

async function registerDecision(id: string, payload: AuditPayload): Promise<ClinicalDocument> {
  const result = await apiRequest<ResultadoTriaje>(`/documents/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
  return normalizeBackendDocument(result)
}

export const auditApi = {
  async obtenerAuditorias(): Promise<ClinicalDocument[]> {
    const data = await apiRequest<{ total: number; items: ResultadoTriaje[] }>(
      '/documents?estado=pendiente_auditoria',
    )
    return data.items.map(normalizeBackendDocument)
  },

  async obtenerAuditoriaPorId(id: string): Promise<ClinicalDocument> {
    const result = await apiRequest<ResultadoTriaje>(`/documents/${encodeURIComponent(id)}`)
    return normalizeBackendDocument(result)
  },

  aprobarAuditoria(id: string): Promise<ClinicalDocument> {
    return registerDecision(id, { decision: 'aprobar', comentario: 'Aprobado por auditoría humana.' })
  },

  rechazarAuditoria(id: string, motivo = 'Rechazado en revisión humana'): Promise<ClinicalDocument> {
    return registerDecision(id, { decision: 'rechazar', comentario: motivo })
  },

  corregirAuditoria(id: string, corrections: AuditCorrection): Promise<ClinicalDocument> {
    return registerDecision(id, {
      decision: 'reclasificar',
      comentario: 'Datos clínicos corregidos durante la auditoría humana.',
      nueva_clasificacion: {
        tipo_documento: corrections.tipo_documento,
        especialidad: corrections.especialidad,
        nivel_prioridad: toBackendPriority(corrections.prioridad),
        destino: toBackendDestination(corrections.destino),
      },
      datos_corregidos: corrections,
    })
  },
}
