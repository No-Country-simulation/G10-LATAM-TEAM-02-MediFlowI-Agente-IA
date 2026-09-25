/**
 * MediFlow - API client wrapper sobre el cliente generado.
 * Este archivo es MANUAL. Wrappea _generated/api/ para agregar
 * lógica de negocio (headers, error handling, etc.)
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'
const API_KEY = import.meta.env.VITE_API_KEY || 'mediflow-dev-secret-key-change-in-prod'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

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
    tipo_documento: string
    especialidad?: string
    nivel_prioridad: 'Urgente' | 'Rutina' | 'Ambiguo'
    score_confianza_clasificacion: number
  }
  datos_extraidos: {
    paciente?: { nombre?: string; edad?: number }
    medico_solicitante?: { nombre?: string; matricula?: string }
    diagnostico_principal?: string
    cie10_sugerido?: string
    hallazgos_clave?: string[]
  }
  decision_enrutamiento: {
    destino_principal: 'Cola_Emergencia_Medica' | 'Cola_Rutina' | 'Cola_Auditoria_Humana'
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
  const res = await fetch(`${API_BASE}/triage`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  })

  if (!res.ok && res.status !== 207) {
    const error = await res.json().catch(() => ({ mensaje: res.statusText }))
    throw new Error(error.mensaje || 'Error al procesar el documento')
  }

  return res.json()
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

  const res = await fetch(`${API_BASE}/triage/upload`, {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY },
    body: form,
  })

  if (!res.ok && res.status !== 207) {
    const error = await res.json().catch(() => ({ mensaje: res.statusText }))
    throw new Error(error.mensaje || 'Error al subir el archivo')
  }

  return res.json()
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

  const res = await fetch(`${API_BASE}/documents?${qs}`, { headers })
  if (!res.ok) throw new Error('Error al listar documentos')
  return res.json()
}

/** Registra decisión de auditoría humana */
export async function registrarAuditoria(
  documentoId: string,
  decision: 'aprobar' | 'rechazar' | 'reclasificar',
  auditorId: string,
  comentario?: string,
): Promise<ResultadoTriaje> {
  const res = await fetch(`${API_BASE}/documents/${documentoId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ decision, auditor_id: auditorId, comentario }),
  })
  if (!res.ok) throw new Error('Error al registrar decisión de auditoría')
  return res.json()
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
  const res = await fetch(`${API_BASE}/settings`, { headers })
  if (!res.ok) throw new Error('Error al obtener la configuración del sistema')
  return res.json()
}

/** Actualiza la configuración del sistema (ej. modo de almacenamiento) */
export async function actualizarConfiguracion(
  storageMode: 'LOCAL' | 'OCI',
): Promise<ConfiguracionSistema> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ storage_mode: storageMode }),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => null)
    if (errorData?.detail?.mensaje) {
      throw new Error(errorData.detail.mensaje)
    }
    if (errorData?.detail && typeof errorData.detail === 'string') {
      throw new Error(errorData.detail)
    }
    throw new Error('Error al actualizar la configuración del sistema')
  }

  return res.json()
}

