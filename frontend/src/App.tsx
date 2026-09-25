import { useState, useEffect } from 'react'
import {
  procesarDocumento,
  subirArchivo,
  listarDocumentos,
  registrarAuditoria,
  obtenerConfiguracion,
  actualizarConfiguracion,
  type ResultadoTriaje,
  type ConfiguracionSistema,
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
  const [activeTab, setActiveTab] = useState<'triage' | 'settings'>('triage')

  const [selectedPresetId, setSelectedPresetId] = useState<string | null>(PRESET_CASES[1].id)

  // Estado del triaje
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

  // Estado de configuración
  const [configSys, setConfigSys] = useState<ConfiguracionSistema | null>(null)
  const [selectedStorageMode, setSelectedStorageMode] = useState<'LOCAL' | 'OCI'>('LOCAL')
  const [savingSettings, setSavingSettings] = useState(false)
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)

  // Cargar estado inicial
  useEffect(() => {
    checkHealth()
    loadRecentDocs()
    loadSettings()
  }, [])

  async function checkHealth() {
    try {
      const res = await fetch('/api/v1/health')
      if (res.ok) {
        const data = await res.json()
        setHealth(data)
      }
    } catch {
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
      // Silencioso
    }
  }

  async function loadSettings() {
    try {
      const sys = await obtenerConfiguracion()
      setConfigSys(sys)
      setSelectedStorageMode(sys.storage_mode as 'LOCAL' | 'OCI')
    } catch {
      // Silencioso
    }
  }

  function handleSelectPreset(preset: (typeof PRESET_CASES)[0]) {
    setSelectedPresetId(preset.id)
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

  async function handleSaveSettings() {
    setSavingSettings(true)
    setSettingsSuccess(null)
    setSettingsError(null)

    try {
      const updated = await actualizarConfiguracion(selectedStorageMode)
      setConfigSys(updated)
      setSettingsSuccess(
        `¡Configuración guardada exitosamente! El almacenamiento físico de documentos ahora es: ${updated.storage_mode}.`,
      )
    } catch (err: any) {
      setSettingsError(err?.message || 'Error al actualizar la configuración.')
    } finally {
      setSavingSettings(false)
    }
  }

  return (
    <div className="mediflow-app">
      {/* ── HEADER & NAVIGATION ────────────────────────────────────────────── */}
      <header className="mediflow-header">
        <div className="brand-group">
          <div>
            <div className="brand-title">
              MediFlow <span className="brand-badge">Agente IA</span>
            </div>
            <div className="brand-subtitle">
              Agente Autónomo de Triaje Clínico Multimodal · LangGraph + Google Gemini
            </div>
          </div>
        </div>

        <div className="header-right-group">
          {/* NAV TABS */}
          <nav className="nav-tabs">
            <button
              type="button"
              className={`nav-tab-btn ${activeTab === 'triage' ? 'active' : ''}`}
              onClick={() => setActiveTab('triage')}
            >
              Triaje Clínico
            </button>
            <button
              type="button"
              className={`nav-tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('settings')
                loadSettings()
              }}
            >
              Configuración
            </button>
          </nav>

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
              Swagger UI
            </a>
          </div>
        </div>
      </header>

      <main className="mediflow-main">
        {/* ─────────────────────────────────────────────────────────────────── */}
        {/* VISTA 1: TRIAJE CLÍNICO                                            */}
        {/* ─────────────────────────────────────────────────────────────────── */}
        {activeTab === 'triage' && (
          <>
            {/* ── PRESETS CASOS DE PRUEBA HACKATHON ─────────────────────────── */}
            <section className="presets-section">
              <div className="section-title-row">
                <h3>Plantillas de Casos de Prueba</h3>
                <span className="section-hint">Haz clic en un caso para cargar su texto en el editor sin procesarlo aún</span>
              </div>

              <div className="presets-grid">
                {PRESET_CASES.map((preset) => {
                  const isSelected = selectedPresetId === preset.id
                  return (
                    <div
                      key={preset.id}
                      className={`preset-card ${isSelected ? 'active-preset' : ''}`}
                      onClick={() => handleSelectPreset(preset)}
                    >
                      <div className="preset-top">
                        <span className={`badge ${preset.badgeColor}`}>{preset.badge}</span>
                        <span className="preset-canal">{preset.canal}</span>
                      </div>
                      <h4 className="preset-title">{preset.titulo}</h4>
                      <p className="preset-desc">{preset.subtitulo}</p>
                      <div className="preset-bottom">
                        <button
                          type="button"
                          className={`btn-use-preset ${isSelected ? 'active-btn' : ''}`}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleSelectPreset(preset)
                          }}
                        >
                          {isSelected ? 'Cargado en Formulario' : 'Cargar Caso'}
                        </button>
                        {isSelected && <span className="active-pill">Activo</span>}
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* ── WORKSPACE: FORMULARIO + RESULTADOS ─────────────────────────── */}
            <div className="workspace-grid">
              {/* COLUMNA IZQUIERDA: INGESTA */}
              <section className="card workspace-form-card">
                <div className="card-header">
                  <h3>Ingesta de Documento Clínico</h3>
                  <button
                    type="button"
                    className="btn-refresh-id"
                    onClick={() => setDocumentoId(`DOC-${Date.now().toString().slice(-6)}`)}
                    title="Generar nuevo ID de documento"
                  >
                    Nuevo ID
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
                        <option value="Guardia_Emergencias">Guardia_Emergencias</option>
                        <option value="Consulta_Externa">Consulta_Externa</option>
                        <option value="Admision">Admision</option>
                        <option value="Cuidados_Intensivos">Cuidados_Intensivos</option>
                        <option value="Laboratorio_Central">Laboratorio_Central</option>
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
                        Texto Clínico
                      </button>
                      <button
                        type="button"
                        className={`toggle-btn ${tipoArchivo !== 'TEXTO' ? 'active' : ''}`}
                        onClick={() => setTipoArchivo('PDF')}
                      >
                        Archivo PDF / Imagen
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
                          {archivo.name} ({(archivo.size / 1024).toFixed(1)} KB)
                        </div>
                      )}
                    </div>
                  )}

                  {error && <div className="alert-error">{error}</div>}

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
                      <>Procesar y Clasificar Documento</>
                    )}
                  </button>
                </form>
              </section>

              {/* COLUMNA DERECHA: RESULTADOS DEL TRIAJE */}
              <section className="card workspace-result-card">
                <div className="card-header">
                  <h3>Decisión y Diagnóstico del Agente</h3>
                  {resultado && (
                    <span className="time-badge">
                      {resultado.tiempo_procesamiento_ms || 35} ms
                    </span>
                  )}
                </div>

                {!resultado && !loading && (
                  <div className="empty-results-state">
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
                            'Cola_Emergencia_Medica' && 'COLA DE EMERGENCIA MÉDICA'}
                          {resultado.decision_enrutamiento.destino_principal === 'Cola_Rutina' &&
                            'COLA DE RUTINA'}
                          {resultado.decision_enrutamiento.destino_principal ===
                            'Cola_Auditoria_Humana' && 'COLA DE AUDITORÍA HUMANA (HITL)'}
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
                          <strong>{resultado.decision_enrutamiento.notificacion_generada.canal}:</strong>{' '}
                          {resultado.decision_enrutamiento.notificacion_generada.mensaje}
                        </div>
                      )}
                    </div>

                    {/* HITL AUDITORÍA HUMANA SI APLICA */}
                    {resultado.decision_enrutamiento.requiere_auditoria_humana && (
                      <div className="hitl-action-box">
                        <h4>Intervención Requerida (Human-in-the-Loop)</h4>
                        <p>El score de confianza o ambigüedad requiere confirmación médica:</p>
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
                          <h5>Hallazgos Clínicos Clave Detectados:</h5>
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
                        <span>Almacenamiento Físico:</span>
                        <code>
                          {resultado.almacenamiento_oci?.ruta_objeto ||
                            `backend/storage/documentos/${resultado.documento_id}.json`}
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

        {/* ─────────────────────────────────────────────────────────────────── */}
        {/* VISTA 2: CONFIGURACIÓN DE ALMACENAMIENTO DE DOCUMENTOS             */}
        {/* ─────────────────────────────────────────────────────────────────── */}
        {activeTab === 'settings' && (
          <div className="settings-view">
            <section className="card settings-card">
              <div className="card-header">
                <h3>Configuración de Almacenamiento de Documentos</h3>
                <span className="section-hint">Preferencia guardada en BD PostgreSQL (<code>configuracion_sistema</code>)</span>
              </div>

              <p className="settings-intro">
                Seleccione dónde se almacenarán físicamente los archivos PDF e imágenes clínicas. Los metadatos, resultados de triaje, estados y registros de auditoría continuarán almacenándose siempre en la base de datos PostgreSQL (`mediflow_dev`).
              </p>

              {settingsSuccess && <div className="alert-success">{settingsSuccess}</div>}
              {settingsError && <div className="alert-error">{settingsError}</div>}

              <div className="storage-options-grid">
                {/* OPCCIÓN LOCAL */}
                <div
                  className={`storage-card ${selectedStorageMode === 'LOCAL' ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedStorageMode('LOCAL')
                    setSettingsError(null)
                  }}
                >
                  <div className="storage-card-header">
                    <input
                      type="radio"
                      id="mode-local"
                      name="storageMode"
                      value="LOCAL"
                      checked={selectedStorageMode === 'LOCAL'}
                      onChange={() => {
                        setSelectedStorageMode('LOCAL')
                        setSettingsError(null)
                      }}
                    />
                    <label htmlFor="mode-local">Almacenamiento Local (Disco del Servidor)</label>
                  </div>
                  <p className="storage-desc">
                    Los documentos PDF e imágenes se almacenarán físicamente en el disco local del servidor backend.
                  </p>
                  <div className="storage-path-info">
                    Ruta: <code>backend/storage/documentos/</code>
                  </div>
                  <div className="storage-status-badge badge-rutina" style={{ marginTop: '10px' }}>
                    Disponible por defecto
                  </div>
                </div>

                {/* OPCCIÓN OCI */}
                <div
                  className={`storage-card ${selectedStorageMode === 'OCI' ? 'selected' : ''} ${
                    configSys && !configSys.oci_configured ? 'card-warning-border' : ''
                  }`}
                  onClick={() => {
                    setSelectedStorageMode('OCI')
                    setSettingsError(null)
                  }}
                >
                  <div className="storage-card-header">
                    <input
                      type="radio"
                      id="mode-oci"
                      name="storageMode"
                      value="OCI"
                      checked={selectedStorageMode === 'OCI'}
                      onChange={() => {
                        setSelectedStorageMode('OCI')
                        setSettingsError(null)
                      }}
                    />
                    <label htmlFor="mode-oci">OCI Object Storage (Oracle Cloud)</label>
                  </div>
                  <p className="storage-desc">
                    Los documentos PDF e imágenes se almacenarán físicamente en el servicio de almacenamiento de objetos de Oracle Cloud.
                  </p>
                  <div className="storage-path-info">
                    Bucket: <code>mediflow-documentos-clinicos</code>
                  </div>
                  {configSys?.oci_configured ? (
                    <div className="storage-status-badge badge-rutina" style={{ marginTop: '10px' }}>
                      Credenciales OCI Configuradas
                    </div>
                  ) : (
                    <div className="storage-status-badge badge-ambiguo" style={{ marginTop: '10px' }}>
                      Credenciales OCI No Configuradas (.env)
                    </div>
                  )}
                </div>
              </div>

              {/* Advertencia si selecciona OCI sin credenciales */}
              {selectedStorageMode === 'OCI' && configSys && !configSys.oci_configured && (
                <div className="alert-warning">
                  <strong>Advertencia OCI:</strong> Las variables de entorno de Oracle Cloud (<code>OCI_USER_OCID</code>, <code>OCI_TENANCY_OCID</code>, <code>OCI_NAMESPACE</code>) no están configuradas en el archivo <code>.env</code>. Si intentas guardar, el backend bloqueará la solicitud.
                </div>
              )}

              <div className="settings-actions">
                <button
                  type="button"
                  className="btn-submit-triage"
                  disabled={savingSettings}
                  onClick={handleSaveSettings}
                >
                  {savingSettings ? (
                    <>
                      <span className="spinner"></span> Guardando en Base de Datos...
                    </>
                  ) : (
                    <>Guardar Preferencia en Base de Datos</>
                  )}
                </button>
              </div>
            </section>

            {/* PANEL DE ESTADO ARQUITECTÓNICO DEL SISTEMA */}
            <section className="card system-info-card">
              <div className="card-header">
                <h3>Estado Arquitectónico de Servicios e Integraciones</h3>
              </div>
              <div className="system-info-grid">
                <div className="info-item">
                  <span className="info-label">Base de Datos Principal:</span>
                  <span className="info-value text-green">
                    {configSys?.database_url_configured ? 'PostgreSQL (mediflow_dev) Siempre Activa' : 'No configurada'}
                  </span>
                  <span className="info-sub">Guarda metadatos, triajes, auditorías HITL y configuraciones</span>
                </div>

                <div className="info-item">
                  <span className="info-label">Almacenamiento Físico de Archivos:</span>
                  <span className="info-value badge-highlight">
                    {configSys?.storage_mode === 'OCI' ? 'OCI Object Storage' : 'Disco Local (Server)'}
                  </span>
                  <span className="info-sub">
                    {configSys?.storage_mode === 'OCI' ? 'Bucket: mediflow-documentos-clinicos' : 'Ruta: backend/storage/documentos/'}
                  </span>
                </div>

                <div className="info-item">
                  <span className="info-label">Proveedor LLM Activo:</span>
                  <span className="info-value">
                    {configSys?.llm_provider || 'Google Gemini'} ({configSys?.llm_configured ? 'Configurado' : 'Modo Simulación / Mock'})
                  </span>
                  <span className="info-sub">Orquestación con LangGraph & Gemini 1.5 Flash</span>
                </div>

                <div className="info-item">
                  <span className="info-label">Estado Credenciales OCI:</span>
                  <span className="info-value">
                    {configSys?.oci_configured ? 'Habilitadas & Listas' : 'No configuradas en .env'}
                  </span>
                  <span className="info-sub">Autenticación por API Key Pem & OCIDs</span>
                </div>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}
