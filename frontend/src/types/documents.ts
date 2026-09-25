import type { ClinicalDocumentType } from '../constants/clinicalDocumentTypes'

export interface Medication {
  nombre?: string
  dosis?: string
  frecuencia?: string
}

export interface ClinicalDocument {
  documento_id: string
  nombre_archivo?: string
  canal_origen?: string
  fecha_creacion?: string
  estado?: string
  url_archivo?: string
  texto_ocr?: string
  clasificacion?: {
    tipo_documento?: ClinicalDocumentType | string
    especialidad?: string
    prioridad?: string
    score_confianza?: number
  }
  datos_extraidos?: {
    paciente?: { nombre?: string; dni?: string; edad?: number | null }
    medico?: { nombre?: string; cmp?: string | null }
    diagnostico?: string
    cie10?: string | null
    estudio_solicitado?: string | null
    medicamentos?: Medication[]
  }
  decision_enrutamiento?: {
    destino?: string
    requiere_auditoria?: boolean
    motivo_auditoria?: string | null
  }
}
