import { normalizeClinicalDocumentType } from '../constants/clinicalDocumentTypes'
import type { ClinicalDocument } from '../types/documents'
import type { ResultadoTriaje } from './triage.api'
import { apiRequest } from './httpClient'

export interface DocumentFilters {
  estado?: string
  tipo?: string
  prioridad?: string
  paciente?: string
}

export interface DashboardSummary {
  procesados: number
  urgentes: number
  auditoria: number
  errores: number
  recientes: ClinicalDocument[]
}

type BackendDocument = ResultadoTriaje & {
  nombre_archivo?: string
  canal_origen?: string
  created_at?: string
  fecha_creacion?: string
  texto_extraido?: string
  texto_ocr?: string
  almacenamiento_oci?: ResultadoTriaje['almacenamiento_oci'] & { nombre_original?: string }
}

export function normalizeBackendDocument(item: BackendDocument): ClinicalDocument {
  const clasificacion = item.clasificacion
  const datos = item.datos_extraidos
  const decision = item.decision_enrutamiento
  const rawPriority = (clasificacion.nivel_prioridad || 'Rutina').toUpperCase()
  const rawStatus = (item.status || 'procesado').toUpperCase()

  return {
    documento_id: item.documento_id,
    nombre_archivo:
      item.nombre_archivo || item.almacenamiento_oci?.nombre_original || `${item.documento_id}.pdf`,
    canal_origen: item.canal_origen || 'Sistema',
    fecha_creacion: item.created_at || item.fecha_creacion,
    estado: rawStatus === 'PENDIENTE_AUDITORIA' ? 'AUDITORIA' : rawStatus,
    clasificacion: {
      tipo_documento: normalizeClinicalDocumentType(clasificacion.tipo_documento),
      especialidad: clasificacion.especialidad || 'Medicina General',
      prioridad:
        rawPriority === 'RUTINA'
          ? 'NORMAL'
          : rawPriority === 'AMBIGUO'
            ? 'PRIORITARIO'
            : rawPriority,
      score_confianza: clasificacion.score_confianza_clasificacion ?? 0,
    },
    datos_extraidos: {
      paciente: {
        nombre: datos.paciente?.nombre || 'Sin identificar',
        dni: datos.paciente?.documento_identidad || '',
        edad: datos.paciente?.edad ?? null,
      },
      medico: {
        nombre: datos.medico_solicitante?.nombre || 'Sin identificar',
        cmp: datos.medico_solicitante?.matricula || null,
      },
      diagnostico: datos.diagnostico_principal || '',
      cie10: datos.cie10_sugerido || null,
      estudio_solicitado: datos.hallazgos_clave?.join(', ') || null,
      medicamentos: [],
    },
    texto_ocr: item.texto_extraido || item.texto_ocr || '',
    decision_enrutamiento: {
      destino: (decision.destino_principal || 'Cola_Rutina').replace(/_/g, ' ').replace('Cola ', ''),
      requiere_auditoria: decision.requiere_auditoria_humana,
      motivo_auditoria: decision.justificacion_enrutamiento || null,
    },
  }
}

function createDocumentId(): string {
  const suffix = crypto.randomUUID().split('-')[0].toUpperCase()
  return `DOC-${new Date().getFullYear()}-${suffix}`
}

function matchesFilters(document: ClinicalDocument, filters: DocumentFilters): boolean {
  if (filters.estado && document.estado?.toUpperCase() !== filters.estado.toUpperCase()) return false
  if (filters.tipo && !document.clasificacion?.tipo_documento?.toLowerCase().includes(filters.tipo.toLowerCase())) return false
  if (filters.prioridad && document.clasificacion?.prioridad?.toUpperCase() !== filters.prioridad.toUpperCase()) return false
  if (filters.paciente) {
    const term = filters.paciente.toLowerCase()
    const patient = document.datos_extraidos?.paciente
    return Boolean(patient?.nombre?.toLowerCase().includes(term) || patient?.dni?.includes(term))
  }
  return true
}

export const documentsApi = {
  async procesarDocumento(file: File, canalOrigen: string): Promise<ClinicalDocument> {
    const form = new FormData()
    form.append('documento_id', createDocumentId())
    form.append('canal_origen', canalOrigen || 'Otro')
    form.append('archivo', file)

    const result = await apiRequest<BackendDocument>('/triage/upload', {
      method: 'POST',
      body: form,
    })
    return normalizeBackendDocument(result)
  },

  async obtenerDocumentos(filters: DocumentFilters = {}): Promise<ClinicalDocument[]> {
    const data = await apiRequest<{ total: number; items: BackendDocument[] }>('/documents')
    return data.items.map(normalizeBackendDocument).filter((document) => matchesFilters(document, filters))
  },

  async obtenerDocumentoPorId(id: string): Promise<ClinicalDocument> {
    if (!id) throw new Error('El identificador del documento es obligatorio.')
    const item = await apiRequest<BackendDocument>(`/documents/${encodeURIComponent(id)}`)
    return normalizeBackendDocument(item)
  },

  async obtenerResumenDashboard(): Promise<DashboardSummary> {
    const documents = await documentsApi.obtenerDocumentos()
    return {
      procesados: documents.filter((document) => document.estado === 'PROCESADO').length,
      urgentes: documents.filter((document) => document.clasificacion?.prioridad === 'URGENTE').length,
      auditoria: documents.filter(
        (document) => document.estado === 'AUDITORIA' || document.decision_enrutamiento?.requiere_auditoria,
      ).length,
      errores: documents.filter(
        (document) => document.estado === 'ERROR' || document.estado === 'RECHAZADO',
      ).length,
      recientes: documents.slice(0, 5),
    }
  },
}
