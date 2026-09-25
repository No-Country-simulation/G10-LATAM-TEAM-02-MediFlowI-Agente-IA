import { useState, useEffect } from 'react'
import {
  procesarDocumento,
  subirArchivo,
  listarDocumentos,
  registrarAuditoria,
  type ResultadoTriaje,
} from './api/triage.api'
import './App.css'

const PRESET_CASES = [
  {
    id: 'CASO-1-RUTINA',
    titulo: 'Caso 1: Rutina',
    subtitulo: 'Analítica de Laboratorio Normal',
    canal: 'Consulta_Externa',
    badge: 'Rutina',
    badgeColor: 'badge-rutina',
    texto: `LABORATORIO CENTRAL — HOSPITAL CLINICO
Paciente: Ana García, 35 años. DNI: 41.234.567.
Médico Solicitante: Dr. Roberto López (Mat. 98231).
Estudio: Hemograma completo y bioquímica básica.
Resultados:
- Hematíes: 4.5 M/uL (Normal)
- Hemoglobina: 14.1 g/dL (Normal)
- Leucocitos: 6.800 /uL (Normal)
- Glucemia: 88 mg/dL (Normal)
- Creatinina: 0.8 mg/dL (Normal)
CONCLUSION: Analítica sin hallazgos patológicos significativos. Parámetros normales.`,
  },
  {
    id: 'CASO-2-URGENCIA',
    titulo: 'Caso 2: Urgencia TEP',
    subtitulo: 'Tromboembolismo Pulmonar Agudo',
    canal: 'Guardia_Emergencias',
    badge: 'Urgencia',
    badgeColor: 'badge-urgencia',
    texto: `HOSPITAL SANTA LUCIA — INFORME DE TOMOGRAFIA COMPUTADA
Paciente: Carlos Eduardo Mendes, 52 años.
Médico Solicitante: Dra. Renata Silveira (Mat. 145892).
Estudio: Angiotomografía de Tórax con contraste endovenoso.
HALLAZGOS:
Marcado defecto de llenado intraluminal en ramas principales de la arteria pulmonar bilateral, con mayor compromiso en lóbulo inferior derecho, compatible con Tromboembolismo Pulmonar Agudo (TEP).
Signos incipientes de sobrecarga ventricular derecha.
CONCLUSION: Tromboembolismo Pulmonar Agudo bilateral de alto riesgo.
NOTIFICACION: Requiere correlación clínica inmediata y atención urgente en Guardia / UCI.`,
  },
  {
    id: 'CASO-3-AMBIGUO',
    titulo: 'Caso 3: Ambiguo / HITL',
    subtitulo: 'Documento Ilegible o Incompleto',
    canal: 'Admision',
    badge: 'Auditoría HITL',
    badgeColor: 'badge-ambiguo',
    texto: `... [MANCHA DE HUMEDAD EN TEXTO] ...
Px: ......... 45a ...
R??: analitica parcial ... hb ??.? ...
Firma medica ilegible ... sello no visible ...
Observaciones: ... mgr ??? ... repetir muestra ...`,
  },
]

interface HealthStatus {
  status: string
  version: string
  llm_disponible: boolean
  oci_disponible: boolean
}

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [documentoId, setDocumentoId] = useState(`DOC-${Date.now().toString().slice(-6)}`)
  const [tipoArchivo, setTipoArchivo] = useState<'TEXTO' | 'PDF' | 'IMAGEN'>('TEXTO')
  const [canalOrigen, setCanalOrigen] = useState('Guardia_Emergencias')
  const [documentoTexto, setDocumentoTexto] = useState(PRESET_CASES[1].texto)
  const [archivo, setArchivo] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [resultado, setResultado] = useState<ResultadoTriaje | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [documentosRecientes, setDocumentosRecientes] = useState<ResultadoTriaje[]>([])
  const [auditSuccess, setAuditSuccess] = useState<string | null>(null)

  // Cargar estado de salud y documentos recientes al inicio
  useEffect(() => {
    checkHealth()
    loadRecentDocs()
  }, [])

  async function checkHealth() {
    try {
      const res = await fetch('/api/v1/health')
      if (res.ok) {
        const data = await res.json()
        setHealth(data)
      }
    } catch {
      // Backend offline o proxy error
      setHealth(null)
    }
  }

  async function loadRecentDocs() {
    try {
      const data = await listarDocumentos({ limit: 10 })
      if (data?.items) {
        setDocumentosRecientes(data.items)
      }
    } catch {
      // Silencioso en carga inicial
    }
  }

  function handleSelectPreset(preset: (typeof PRESET_CASES)[0]) {
    setDocumentoId(`DOC-${Date.now().toString().slice(-6)}`)
    setCanalOrigen(preset.canal)
    setTipoArchivo('TEXTO')
    setDocumentoTexto(preset.texto)
    setArchivo(null)
    setError(null)
  }

  async function handleEjecutarTriage(e?: React.FormEvent) {
    if (e) e.preventDefault()
    setLoading(true)
    setError(null)
    setAuditSuccess(null)

    try {
      let res: ResultadoTriaje
      if (tipoArchivo === 'TEXTO' || !archivo) {
        res = await procesarDocumento({
          documento_id: documentoId,
          tipo_archivo: 'TEXTO',
          documento_texto: documentoTexto,
          canal_origen: canalOrigen,
        })
      } else {
        res = await subirArchivo(documentoId, canalOrigen, archivo)
      }
      setResultado(res)
      loadRecentDocs()
    } catch (err: any) {
      setError(err?.message || 'Error al ejecutar el triaje.')
    } finally {
      setLoading(false)
    }
  }

  async function handleAuditoria(decision: 'aprobar' | 'rechazar' | 'reclasificar') {
    if (!resultado) return
    try {
      const updated = await registrarAuditoria(
        resultado.documento_id,
        decision,
        'Auditor-Médico-DrPerez',
        `Decisión manual aplicada: ${decision}`,
      )
      setResultado(updated)
      setAuditSuccess(`Decisión de auditoría "${decision.toUpperCase()}" registrada correctamente.`)
      loadRecentDocs()
    } catch (err: any) {
      setError(err?.message || 'Error al guardar la auditoría.')
    }
  }

  return (
    <div className="mediflow-app">
      {/* ── HEADER ────────────────────────────────────────────────────────── */}
      <header className="mediflow-header">
        <div className="brand-group">
          <div className="brand-logo">🏥</div>
          <div>
            <div className="brand-title">
              MediFlow <span className="brand-badge">Agente IA</span>
            </div>
            <div className="brand-subtitle">
              Agente Autónomo de Triaje Clínico Multimodal · LangGraph + Google Gemini
            </div>
          </div>
        </div>

        <div className="header-status">
          {health ? (
            <div className="status-pill status-online">
              <span className="dot dot-green"></span>
              <span>Backend v{health.version} Activo</span>
            </div>
          ) : (
            <div className="status-pill status-offline">
              <span className="dot dot-red"></span>
              <span>Backend Desconectado</span>
            </div>
          )}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="btn-api-docs"
          >
            📖 Swagger UI
          </a>
        </div>
      </header>

      <main className="mediflow-main">
        {/* ── PRESETS CASOS DE PRUEBA HACKATHON ─────────────────────────────── */}
        <section className="presets-section">
          <div className="section-title-row">
            <h3>⚡ Casos de Prueba Oficiales (Hackathon ONE G10)</h3>
            <span className="section-hint">Selecciona un caso para autocompletar</span>
          </div>

          <div className="presets-grid">
            {PRESET_CASES.map((preset) => (
              <div
                key={preset.id}
                className="preset-card"
                onClick={() => handleSelectPreset(preset)}
              >
                <div className="preset-top">
                  <span className={`badge ${preset.badgeColor}`}>{preset.badge}</span>
                  <span className="preset-canal">{preset.canal}</span>
                </div>
                <h4 className="preset-title">{preset.titulo}</h4>
                <p className="preset-desc">{preset.subtitulo}</p>
                <button
                  type="button"
                  className="btn-use-preset"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleSelectPreset(preset)
                  }}
                >
                  Cargar Caso →
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* ── WORKSPACE: FORMULARIO + RESULTADOS ─────────────────────────────── */}
        <div className="workspace-grid">
          {/* COLUMNA IZQUIERDA: INGESTA */}
          <section className="card workspace-form-card">
            <div className="card-header">
              <h3>📥 Ingesta de Documento Clínico</h3>
              <button
                type="button"
                className="btn-refresh-id"
                onClick={() => setDocumentoId(`DOC-${Date.now().toString().slice(-6)}`)}
                title="Generar nuevo ID de documento"
              >
                🔄 Nuevo ID
              </button>
            </div>

            <form onSubmit={handleEjecutarTriage} className="triage-form">
              <div className="form-row">
                <div className="form-group flex-1">
                  <label htmlFor="doc-id">ID Documento</label>
                  <input
                    id="doc-id"
                    type="text"
                    value={documentoId}
                    onChange={(e) => setDocumentoId(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group flex-1">
                  <label htmlFor="canal-origen">Canal de Origen</label>
                  <select
                    id="canal-origen"
                    value={canalOrigen}
                    onChange={(e) => setCanalOrigen(e.target.value)}
                  >
                    <option value="Guardia_Emergencias">🚨 Guardia_Emergencias</option>
                    <option value="Consulta_Externa">🩺 Consulta_Externa</option>
                    <option value="Admision">📋 Admision</option>
                    <option value="Cuidados_Intensivos">🏥 Cuidados_Intensivos</option>
                    <option value="Laboratorio_Central">🔬 Laboratorio_Central</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Tipo de Entrada</label>
                <div className="type-toggle-group">
                  <button
                    type="button"
                    className={`toggle-btn ${tipoArchivo === 'TEXTO' ? 'active' : ''}`}
                    onClick={() => setTipoArchivo('TEXTO')}
                  >
                    📝 Texto Clínico
                  </button>
                  <button
                    type="button"
                    className={`toggle-btn ${tipoArchivo !== 'TEXTO' ? 'active' : ''}`}
                    onClick={() => setTipoArchivo('PDF')}
                  >
                    📎 Archivo PDF / Imagen
                  </button>
                </div>
              </div>

              {tipoArchivo === 'TEXTO' ? (
                <div className="form-group">
                  <label htmlFor="doc-text">Contenido del Documento Clínico</label>
                  <textarea
                    id="doc-text"
                    rows={8}
                    value={documentoTexto}
                    onChange={(e) => setDocumentoTexto(e.target.value)}
                    placeholder="Pega aquí el informe médico, análisis de laboratorio o nota clínica..."
                    required
                  />
                </div>
              ) : (
                <div className="form-group">
                  <label htmlFor="file-input">Seleccionar Archivo (PDF o Imagen)</label>
                  <input
                    id="file-input"
                    type="file"
                    accept=".pdf,image/png,image/jpeg,image/webp"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setArchivo(e.target.files[0])
                      }
                    }}
                  />
                  {archivo && (
                    <div className="file-info-box">
                      📄 {archivo.name} ({(archivo.size / 1024).toFixed(1)} KB)
                    </div>
                  )}
                </div>
              )}

              {error && <div className="alert-error">⚠️ {error}</div>}

              <button
                type="submit"
                className="btn-submit-triage"
                disabled={loading || (tipoArchivo === 'TEXTO' && !documentoTexto.trim())}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Analizando con LangGraph & Gemini...
                  </>
                ) : (
                  <>🚀 Ejecutar Triaje Autónomo</>
                )}
              </button>
            </form>
          </section>

          {/* COLUMNA DERECHA: RESULTADOS DEL TRIAJE */}
          <section className="card workspace-result-card">
            <div className="card-header">
              <h3>🎯 Decisión y Diagnóstico del Agente</h3>
              {resultado && (
                <span className="time-badge">
                  ⏱️ {resultado.tiempo_procesamiento_ms || 35} ms
                </span>
              )}
            </div>

            {!resultado && !loading && (
              <div className="empty-results-state">
                <div className="empty-icon">🩺</div>
                <h4>Ningún documento analizado aún</h4>
                <p>
                  Selecciona uno de los <strong>Casos de Prueba Hackathon</strong> arriba o escribe
                  un texto clínico para que el agente LangGraph realice la extracción, clasificación
                  y enrutamiento autónomo.
                </p>
              </div>
            )}

            {loading && (
              <div className="processing-state">
                <div className="big-spinner"></div>
                <h4>Agente MediFlow Procesando</h4>
                <div className="steps-flow">
                  <div className="flow-node active">1. Ingestión</div>
                  <div className="flow-arrow">→</div>
                  <div className="flow-node active">2. Extracción</div>
                  <div className="flow-arrow">→</div>
                  <div className="flow-node active">3. Clasificación</div>
                  <div className="flow-arrow">→</div>
                  <div className="flow-node active">4. Confianza</div>
                  <div className="flow-arrow">→</div>
                  <div className="flow-node active">5. Enrutamiento</div>
                </div>
              </div>
            )}

            {resultado && !loading && (
              <div className="results-content">
                {/* BANNER DE DECISIÓN DE ENRUTAMIENTO */}
                <div
                  className={`routing-banner ${
                    resultado.decision_enrutamiento.destino_principal === 'Cola_Emergencia_Medica'
                      ? 'banner-urgente'
                      : resultado.decision_enrutamiento.destino_principal === 'Cola_Rutina'
                        ? 'banner-rutina'
                        : 'banner-ambiguo'
                  }`}
                >
                  <div className="banner-top">
                    <span className="destination-badge">
                      {resultado.decision_enrutamiento.destino_principal ===
                        'Cola_Emergencia_Medica' && '🚨 COLA DE EMERGENCIA MÉDICA'}
                      {resultado.decision_enrutamiento.destino_principal === 'Cola_Rutina' &&
                        '✅ COLA DE RUTINA'}
                      {resultado.decision_enrutamiento.destino_principal ===
                        'Cola_Auditoria_Humana' && '⚠️ COLA DE AUDITORÍA HUMANA (HITL)'}
                    </span>
                    <span className="score-badge">
                      Score Confianza:{' '}
                      {(resultado.clasificacion.score_confianza_clasificacion * 100).toFixed(0)}%
                    </span>
                  </div>

                  <p className="justification-text">
                    <strong>Motivo:</strong>{' '}
                    {resultado.decision_enrutamiento.justificacion_enrutamiento}
                  </p>

                  {resultado.decision_enrutamiento.notificacion_generada && (
                    <div className="notification-box">
                      🔔 <strong>{resultado.decision_enrutamiento.notificacion_generada.canal}:</strong>{' '}
                      {resultado.decision_enrutamiento.notificacion_generada.mensaje}
                    </div>
                  )}
                </div>

                {/* HITL AUDITORÍA HUMANA SI APLICA */}
                {resultado.decision_enrutamiento.requiere_auditoria_humana && (
                  <div className="hitl-action-box">
                    <h4>👨‍⚕️ Intervención Requerida (Human-in-the-Loop)</h4>
                    <p>El score de confianza o ambigüedad requiere confirmación médica:</p>
                    <div className="hitl-btn-group">
                      <button
                        type="button"
                        className="btn-hitl btn-hitl-aprobar"
                        onClick={() => handleAuditoria('aprobar')}
                      >
                        ✓ Aprobar
                      </button>
                      <button
                        type="button"
                        className="btn-hitl btn-hitl-reclasificar"
                        onClick={() => handleAuditoria('reclasificar')}
                      >
                        🔄 Reclasificar
                      </button>
                      <button
                        type="button"
                        className="btn-hitl btn-hitl-rechazar"
                        onClick={() => handleAuditoria('rechazar')}
                      >
                        ✕ Rechazar
                      </button>
                    </div>
                    {auditSuccess && <div className="audit-success-msg">{auditSuccess}</div>}
                  </div>
                )}

                {/* ENTIDADES EXTRAÍDAS */}
                <div className="entities-grid">
                  <div className="entity-card">
                    <h5>👤 Paciente</h5>
                    <div className="entity-val">
                      {resultado.datos_extraidos.paciente?.nombre || 'No especificado'}
                    </div>
                    <div className="entity-sub">
                      Edad:{' '}
                      {resultado.datos_extraidos.paciente?.edad !== undefined &&
                      resultado.datos_extraidos.paciente?.edad !== null
                        ? `${resultado.datos_extraidos.paciente.edad} años`
                        : 'N/D'}
                    </div>
                  </div>

                  <div className="entity-card">
                    <h5>🩺 Médico Solicitante</h5>
                    <div className="entity-val">
                      {resultado.datos_extraidos.medico_solicitante?.nombre || 'No especificado'}
                    </div>
                    <div className="entity-sub">
                      Matrícula:{' '}
                      {resultado.datos_extraidos.medico_solicitante?.matricula || 'N/D'}
                    </div>
                  </div>

                  <div className="entity-card entity-card-wide">
                    <h5>📋 Diagnóstico & CIE-10</h5>
                    <div className="entity-val highlight-diag">
                      {resultado.datos_extraidos.diagnostico_principal ||
                        resultado.clasificacion.tipo_documento ||
                        'En evaluación'}
                    </div>
                    {resultado.datos_extraidos.cie10_sugerido && (
                      <span className="cie10-pill">
                        CIE-10: {resultado.datos_extraidos.cie10_sugerido}
                      </span>
                    )}
                  </div>
                </div>

                {/* HALLAZGOS CLAVE */}
                {resultado.datos_extraidos.hallazgos_clave &&
                  resultado.datos_extraidos.hallazgos_clave.length > 0 && (
                    <div className="findings-section">
                      <h5>🔍 Hallazgos Clínicos Clave Detectados:</h5>
                      <ul className="findings-list">
                        {resultado.datos_extraidos.hallazgos_clave.map((h, i) => (
                          <li key={i}>{h}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* DETALLES DE ALMACENAMIENTO & TRAZABILIDAD */}
                <div className="trace-footer">
                  <div className="trace-item">
                    <span>Persistencia OCI / Local:</span>
                    <code>
                      {resultado.almacenamiento_oci?.ruta_objeto ||
                        `procesados/${resultado.documento_id}.json`}
                    </code>
                  </div>
                  <div className="trace-item">
                    <span>Trazabilidad LangGraph:</span>
                    <span className="nodes-pills">
                      {['ingestion', 'extraction', 'classification', 'confidence', 'routing'].map(
                        (nodo) => (
                          <span key={nodo} className="node-pill">
                            {nodo}
                          </span>
                        ),
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>

        {/* ── TABLA DE DOCUMENTOS PROCESADOS RECIENTES ───────────────────────── */}
        {documentosRecientes.length > 0 && (
          <section className="card history-section">
            <div className="card-header">
              <h3>📂 Historial de Documentos Procesados</h3>
              <button type="button" className="btn-secondary" onClick={loadRecentDocs}>
                Refrescar
              </button>
            </div>
            <div className="table-wrapper">
              <table className="docs-table">
                <thead>
                  <tr>
                    <th>ID Documento</th>
                    <th>Prioridad</th>
                    <th>Destino Asignado</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {documentosRecientes.map((doc, idx) => (
                    <tr key={idx}>
                      <td>
                        <code>{doc.documento_id}</code>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            doc.clasificacion?.nivel_prioridad === 'Urgente'
                              ? 'badge-urgencia'
                              : doc.clasificacion?.nivel_prioridad === 'Rutina'
                                ? 'badge-rutina'
                                : 'badge-ambiguo'
                          }`}
                        >
                          {doc.clasificacion?.nivel_prioridad || 'Ambiguo'}
                        </span>
                      </td>
                      <td>{doc.decision_enrutamiento?.destino_principal}</td>
                      <td>
                        {(
                          (doc.clasificacion?.score_confianza_clasificacion || 0) * 100
                        ).toFixed(0)}
                        %
                      </td>
                      <td>
                        <span
                          className={`status-indicator ${
                            doc.status === 'procesado' ? 'text-green' : 'text-amber'
                          }`}
                        >
                          {doc.status}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn-inspect"
                          onClick={() => setResultado(doc)}
                        >
                          Ver Detalle
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
