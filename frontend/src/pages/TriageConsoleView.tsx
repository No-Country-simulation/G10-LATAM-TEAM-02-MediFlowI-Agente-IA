import { useState, useEffect } from 'react'
import {
  procesarDocumento,
  subirArchivo,
  listarDocumentos,
  registrarAuditoria,
  type ResultadoTriaje,
} from '../api/triage.api'
import { useAuth } from '../hooks/useAuth'
import { normalizeClinicalDocumentType } from '../constants/clinicalDocumentTypes'
import '../App.css'

const PRESET_CASES = [
  {
    id: 'CASO-1-RUTINA',
    titulo: 'Caso 1: Rutina',
    subtitulo: 'Analítica de Laboratorio Normal',
    canal: 'Consulta_Externa',
    badge: 'Rutina',
    badgeColor: 'badge-rutina',
    texto: `LABORATORIO CENTRAL - HOSPITAL CLINICO
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
    texto: `HOSPITAL SANTA LUCIA - INFORME DE TOMOGRAFIA COMPUTADA
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
    texto: `DOCUMENTO CLINICO INCOMPLETO
Paciente: Marcos V.
Estudio: Evaluación preliminar.
Notas: Manuscrito borroso. Se identifican valores fuera de rango no especificados. Requiere auditoría humana para determinar nivel de urgencia o reclasificar especialidad.`,
  },
]

const createDocumentId = () => `DOC-${Math.floor(100000 + Math.random() * 900000)}`

interface TriageConsoleViewProps {
  initialTab?: 'triage' | 'users' | 'settings'
  hideInnerMenu?: boolean
}

export default function TriageConsoleView({ initialTab = 'triage', hideInnerMenu = true }: TriageConsoleViewProps) {
  const { user: currentUser, logout } = useAuth()

  // ── NAVEGACIÓN Y VISTAS ────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<'triage' | 'users' | 'settings'>(initialTab)

  // ── ESTADO DE TRIAJE ───────────────────────────────────────────────
  const [activePreset, setActivePreset] = useState<string>('CASO-1-RUTINA')
  const [docId, setDocId] = useState(createDocumentId)
  const [canalOrigen, setCanalOrigen] = useState('Consulta_Externa')
  const [tipoEntrada, setTipoEntrada] = useState<'texto' | 'archivo'>('texto')
  const [textoClinico, setTextoClinico] = useState(PRESET_CASES[0].texto)
  const [fileToUpload, setFileToUpload] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resultado, setResultado] = useState<ResultadoTriaje | null>(null)
  const [auditSuccess, setAuditSuccess] = useState<string | null>(null)
  const [documentosRecientes, setDocumentosRecientes] = useState<ResultadoTriaje[]>([])
  const generateNewId = () => {
    setDocId(createDocumentId())
  }

  const handleSelectPreset = (presetId: string) => {
    const p = PRESET_CASES.find((c) => c.id === presetId)
    if (p) {
      setActivePreset(presetId)
      setCanalOrigen(p.canal)
      setTextoClinico(p.texto)
      setTipoEntrada('texto')
      setResultado(null)
      setError(null)
      setAuditSuccess(null)
      generateNewId()
    }
  }

  const loadRecentDocs = async () => {
    try {
      const res = await listarDocumentos({ limit: 10 })
      setDocumentosRecientes(res.items || [])
    } catch (e) {
      console.error('Error cargando historial de documentos:', e)
    }
  }

  useEffect(() => {
    listarDocumentos({ limit: 10 })
      .then((res) => setDocumentosRecientes(res.items || []))
      .catch((error: unknown) => console.error('Error cargando historial de documentos:', error))
  }, [])

  const handleLogout = () => {
    logout()
    setActiveTab('triage')
  }

  // Procesar Triaje
  const handleSubmitTriage = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResultado(null)
    setAuditSuccess(null)

    try {
      let res: ResultadoTriaje
      if (tipoEntrada === 'archivo' && fileToUpload) {
        res = await subirArchivo(docId, canalOrigen, fileToUpload)
      } else {
        res = await procesarDocumento({
          documento_id: docId,
          canal_origen: canalOrigen,
          tipo_archivo: 'TEXTO',
          documento_texto: textoClinico,
        })
      }
      setResultado(res)
      loadRecentDocs()
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Ocurrió un error inesperado al clasificar el documento.')
    } finally {
      setLoading(false)
    }
  }

  // HITL Auditoría
  const handleAuditoria = async (decision: 'aprobar' | 'reclasificar' | 'rechazar') => {
    if (!resultado) return
    try {
      await registrarAuditoria(
        resultado.documento_id,
        decision,
        `Decisión de auditoría ejecutada por ${currentUser ? currentUser.nombres : 'Auditor Médica'} (${currentUser ? currentUser.rol : 'AUDITOR'}).`
      )
      setAuditSuccess(`Auditoría registrada: Decisión "${decision.toUpperCase()}" enviada.`)
      loadRecentDocs()
    } catch (error) {
      setError('Error al registrar auditoría: ' + (error instanceof Error ? error.message : 'Error inesperado'))
    }
  }





  // ── RENDERING RESTRICCIONES POR ROL (RF-05) ──────────────────────────
  const canUploadDocs = !currentUser || currentUser.rol === 'ADMINISTRADOR' || currentUser.rol === 'OPERADOR'
  const canAuditHITL = !currentUser || currentUser.rol === 'ADMINISTRADOR' || currentUser.rol === 'AUDITOR' || currentUser.rol === 'SUPERVISOR'
  const isSupervisorReadOnly = currentUser?.rol === 'SUPERVISOR'
  const canManageUsers = currentUser?.rol === 'ADMINISTRADOR'
  const canManageSettings = currentUser?.rol === 'ADMINISTRADOR'

  return (
    <div className="app-container">
      {/* ── HEADER PRINCIPAL (Solo cuando NO se oculta el menú interno) ──── */}
      {!hideInnerMenu && (
        <header className="app-header">
          <div className="header-brand">
            <h2>MediFlow</h2>
            <span className="badge-agent">Agente Autónomo de Triaje Clínico</span>
          </div>

          {/* CONTROLES DE SESIÓN & BADGE DE USUARIO */}
          <div className="header-actions">
            {currentUser && (
              <div className="user-profile-badge">
                <div className="user-info">
                  <span className="user-name">{currentUser.nombres} {currentUser.apellidos}</span>
                  <span className="user-dni">DNI: <strong>{currentUser.documento_identidad}</strong></span>
                </div>
                <span className={`role-pill role-${currentUser.rol.toLowerCase()}`}>
                  {currentUser.rol}
                </span>
                <button type="button" className="btn-logout" onClick={handleLogout}>
                  Cerrar Sesión
                </button>
              </div>
            )}
          </div>
        </header>
      )}

      {/* ── CONTENIDO PRINCIPAL ───────────────── */}
      <div className="console-layout-wrapper">
        {currentUser && !hideInnerMenu && (
          <aside className="vertical-console-menu">
            <div className="menu-header">
              <span className="menu-title">Menú de Consola</span>
            </div>
            <nav className="vertical-nav-list">
              <button
                type="button"
                className={`vertical-nav-item ${activeTab === 'triage' ? 'active' : ''}`}
                onClick={() => setActiveTab('triage')}
              >
                <div className="nav-text">
                  <strong>Triaje Clínico</strong>
                  <small>Carga & Diagnóstico IA</small>
                </div>
              </button>

              {canManageUsers && (
                <button
                  type="button"
                  className={`vertical-nav-item ${activeTab === 'users' ? 'active' : ''}`}
                  onClick={() => setActiveTab('users')}
                >
                  <div className="nav-text">
                    <strong>Gestión de Usuarios</strong>
                    <small>Control de Acceso RBAC</small>
                  </div>
                </button>
              )}

              {canManageSettings && (
                <button
                  type="button"
                  className={`vertical-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
                  onClick={() => setActiveTab('settings')}
                >
                  <div className="nav-text">
                    <strong>Configuración</strong>
                    <small>Almacenamiento Local/OCI</small>
                  </div>
                </button>
              )}
            </nav>
          </aside>
        )}

        <main className="console-content-area">
        {/* ─────────────────────────────────────────────────────────────────── */}
        {/* VISTA 1: TRIAJE CLÍNICO (CARGA & EVALUACIÓN MULTIMODAL)              */}
        {/* ─────────────────────────────────────────────────────────────────── */}
        {activeTab === 'triage' && (
          <>
            {/* PLANTILLAS DE PRUEBA */}
            {canUploadDocs && (
              <section className="card presets-card">
                <div className="card-header">
                  <h3>Plantillas de Casos de Prueba</h3>
                  <span className="section-hint">Haz clic en un caso para cargar su texto en el editor</span>
                </div>
                <div className="presets-grid">
                  {PRESET_CASES.map((preset) => (
                    <button
                      type="button"
                      key={preset.id}
                      className={`preset-item ${activePreset === preset.id ? 'active-preset' : ''}`}
                      onClick={() => handleSelectPreset(preset.id)}
                      aria-pressed={activePreset === preset.id}
                    >
                      <div className="preset-item-header">
                        <span className={`badge ${preset.badgeColor}`}>{preset.badge}</span>
                        <span className="preset-channel">{preset.canal}</span>
                      </div>
                      <h4>{preset.titulo}</h4>
                      <p className="preset-sub">{preset.subtitulo}</p>
                      <div className="preset-btn-wrapper">
                        <span className={`btn-preset-action ${activePreset === preset.id ? 'active-btn' : ''}`}>
                          {activePreset === preset.id ? 'Cargado en Formulario' : 'Cargar Caso'}
                        </span>
                        {activePreset === preset.id && <span className="active-pill">Activo</span>}
                      </div>
                    </button>
                  ))}
                </div>
              </section>
            )}

            {/* PANEL DE FORMULARIO E INGESTA */}
            <div className="workspace-grid">
              {canUploadDocs ? (
                <section className="card form-card">
                  <div className="card-header">
                    <h3>Ingesta de Documento Clínico</h3>
                    <button type="button" className="btn-secondary" onClick={generateNewId}>
                      Nuevo ID
                    </button>
                  </div>

                  <form onSubmit={handleSubmitTriage}>
                    <div className="form-row">
                      <div className="form-group">
                        <label htmlFor="doc-id">ID Documento</label>
                        <input
                          id="doc-id"
                          type="text"
                          value={docId}
                          onChange={(e) => setDocId(e.target.value)}
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label htmlFor="canal-origen">Canal de Origen</label>
                        <select
                          id="canal-origen"
                          value={canalOrigen}
                          onChange={(e) => setCanalOrigen(e.target.value)}
                        >
                          <option value="Guardia_Emergencias">Guardia_Emergencias</option>
                          <option value="Consulta_Externa">Consulta_Externa</option>
                          <option value="Admision">Admision</option>
                          <option value="Laboratorio">Laboratorio</option>
                        </select>
                      </div>
                    </div>

                    <div className="form-group">
                      <label>Tipo de Entrada</label>
                      <div className="toggle-group">
                        <button
                          type="button"
                          className={`toggle-btn ${tipoEntrada === 'texto' ? 'selected' : ''}`}
                          onClick={() => setTipoEntrada('texto')}
                        >
                          Texto Clínico
                        </button>
                        <button
                          type="button"
                          className={`toggle-btn ${tipoEntrada === 'archivo' ? 'selected' : ''}`}
                          onClick={() => setTipoEntrada('archivo')}
                        >
                          Archivo PDF / Imagen
                        </button>
                      </div>
                    </div>

                    {tipoEntrada === 'texto' ? (
                      <div className="form-group">
                        <label htmlFor="contenido-texto">Contenido del Documento Clínico</label>
                        <textarea
                          id="contenido-texto"
                          rows={10}
                          value={textoClinico}
                          onChange={(e) => setTextoClinico(e.target.value)}
                          placeholder="Ingrese o pegue el informe médico, análisis de laboratorio o nota de evolución..."
                          required
                        />
                      </div>
                    ) : (
                      <div className="form-group">
                        <label htmlFor="archivo-input">Seleccionar Archivo (PDF, PNG, JPG)</label>
                        <input
                          id="archivo-input"
                          type="file"
                          accept=".pdf,.png,.jpg,.jpeg"
                          onChange={(e) => setFileToUpload(e.target.files?.[0] || null)}
                          required
                        />
                        {fileToUpload && (
                          <div className="file-info">
                            Archivo seleccionado: <strong>{fileToUpload.name}</strong> (
                            {(fileToUpload.size / 1024).toFixed(1)} KB)
                          </div>
                        )}
                      </div>
                    )}

                    {error && <div className="alert-error">{error}</div>}

                    <button type="submit" className="btn-submit-triage" disabled={loading}>
                      {loading ? (
                        <>
                          <span className="spinner"></span> Analizando con LangGraph & Gemini...
                        </>
                      ) : (
                        <>Procesar y Clasificar Documento</>
                      )}
                    </button>
                  </form>
                </section>
              ) : (
                <section className="card form-card">
                  <div className="card-header">
                    <h3>Acceso en Modo Consulta</h3>
                  </div>
                  <p>Su rol actual (<strong>{currentUser?.rol}</strong>) le permite visualizar diagnósticos e historiales pero no cargar nuevos documentos.</p>
                </section>
              )}

              {/* PANEL DE RESULTADOS DE DIAGNÓSTICO Y ACCIÓN HITL */}
              <section className="card result-card">
                <div className="card-header">
                  <h3>Decisión y Diagnóstico del Agente</h3>
                  {resultado && (
                    <span className="result-time">{resultado.tiempo_procesamiento_ms} ms</span>
                  )}
                </div>

                {!resultado && !loading && (
                  <div className="empty-state">
                    <p>Complete el formulario y presione "Procesar y Clasificar Documento" para visualizar el diagnóstico autónomo.</p>
                  </div>
                )}

                {loading && (
                  <div className="loading-state">
                    <div className="spinner-large"></div>
                    <p>Ejecutando nodos de LangGraph: Ingesta ➔ Extracción ➔ Clasificación ➔ Evaluación ➔ Enrutamiento...</p>
                  </div>
                )}

                {resultado && (
                  <div className="result-body">
                    {/* ENCABEZADO DE ENRUTAMIENTO */}
                    <div
                      className={`decision-banner ${
                        resultado.clasificacion.nivel_prioridad === 'Urgente'
                          ? 'banner-urgente'
                          : resultado.clasificacion.nivel_prioridad === 'Rutina'
                            ? 'banner-rutina'
                            : 'banner-ambiguo'
                      }`}
                    >
                      <div className="banner-top">
                        <span className="destination-title">
                          {resultado.decision_enrutamiento.destino_principal.replace(/_/g, ' ').toUpperCase()}
                        </span>
                        <span className="confidence-score">
                          Score Confianza:{' '}
                          {(
                            resultado.clasificacion.score_confianza_clasificacion * 100
                          ).toFixed(0)}
                          %
                        </span>
                      </div>

                      <p className="justification-text">
                        <strong>Motivo:</strong>{' '}
                        {resultado.decision_enrutamiento.justificacion_enrutamiento}
                      </p>
                    </div>

                    {/* HITL AUDITORÍA HUMANA SI APLICA (RF-05) */}
                    {resultado.decision_enrutamiento.requiere_auditoria_humana && canAuditHITL && (
                      <div className="hitl-action-box">
                        <h4>Intervención Requerida (Human-in-the-Loop)</h4>
                        <p>El score de confianza o ambigüedad requiere confirmación médica:</p>

                        {!isSupervisorReadOnly ? (
                          <div className="hitl-btn-group">
                            <button
                              type="button"
                              className="btn-hitl btn-hitl-aprobar"
                              onClick={() => handleAuditoria('aprobar')}
                            >
                              Aprobar
                            </button>
                            <button
                              type="button"
                              className="btn-hitl btn-hitl-reclasificar"
                              onClick={() => handleAuditoria('reclasificar')}
                            >
                              Reclasificar
                            </button>
                            <button
                              type="button"
                              className="btn-hitl btn-hitl-rechazar"
                              onClick={() => handleAuditoria('rechazar')}
                            >
                              Rechazar
                            </button>
                          </div>
                        ) : (
                          <div className="read-only-hint">
                            (Rol SUPERVISOR: Solo consulta de decisiones de auditoría)
                          </div>
                        )}
                        {auditSuccess && <div className="audit-success-msg">{auditSuccess}</div>}
                      </div>
                    )}

                    {/* ENTIDADES EXTRAÍDAS */}
                    <div className="entities-grid">
                      <div className="entity-card">
                        <h5>Paciente</h5>
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
                        <h5>Médico Solicitante</h5>
                        <div className="entity-val">
                          {resultado.datos_extraidos.medico_solicitante?.nombre || 'No especificado'}
                        </div>
                        <div className="entity-sub">
                          Matrícula:{' '}
                          {resultado.datos_extraidos.medico_solicitante?.matricula || 'N/D'}
                        </div>
                      </div>

                      <div className="entity-card entity-card-wide">
                        <h5>Diagnóstico & CIE-10</h5>
                        <div className="entity-val highlight-diag">
                          {resultado.datos_extraidos.diagnostico_principal ||
                            normalizeClinicalDocumentType(resultado.clasificacion.tipo_documento)}
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
                          <h5>Hallazgos Clínicos Clave Detectados:</h5>
                          <ul className="findings-list">
                            {resultado.datos_extraidos.hallazgos_clave.map((h, i) => (
                              <li key={i}>{h}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                  </div>
                )}
              </section>
            </div>

            {/* ── TABLA DE DOCUMENTOS PROCESADOS RECIENTES ───────────────────────── */}
            {documentosRecientes.length > 0 && (
              <section className="card history-section">
                <div className="card-header">
                  <h3>Historial de Documentos Procesados</h3>
                  <button type="button" className="btn-secondary" onClick={loadRecentDocs}>
                    Refrescar
                  </button>
                </div>
                <div className="table-wrapper">
                  <table className="docs-table">
                    <thead>
                      <tr>
                        <th>ID Documento</th>
                        <th>Fecha de Procesamiento</th>
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
                            <span className="doc-date">
                              {doc.created_at
                                ? new Date(doc.created_at).toLocaleString('es-ES', {
                                    dateStyle: 'short',
                                    timeStyle: 'medium',
                                  })
                                : 'Hace un momento'}
                            </span>
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
          </>
        )}
      </main>
      </div>
    </div>
  )
}
