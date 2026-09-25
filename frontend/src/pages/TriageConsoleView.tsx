import { useState, useEffect } from 'react'
import {
  procesarDocumento,
  subirArchivo,
  listarDocumentos,
  registrarAuditoria,
  type ResultadoTriaje,
} from '../api/triage.api'
import {
  loginUser,
  logoutUser,
  getCurrentUser,
  type User,
} from '../api/auth.api'
import { useAuth } from '../hooks/useAuth'
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

const QUICK_USERS = [
  { label: 'Administrador (Full Access)', dni: '12345678', pwd: 'admin' },
  { label: 'Operador (Carga & Triaje)', dni: '87654321', pwd: 'operador' },
  { label: 'Auditor (Revisión HITL)', dni: '11223344', pwd: 'auditor' },
  { label: 'Supervisor (Lectura & KPI)', dni: '44332211', pwd: 'supervisor' },
]



interface TriageConsoleViewProps {
  initialTab?: 'triage' | 'users' | 'settings'
  hideInnerMenu?: boolean
}

export default function TriageConsoleView({ initialTab = 'triage', hideInnerMenu = true }: TriageConsoleViewProps) {
  const { user: globalAuthUser } = useAuth()

  // ── ESTADO DE AUTENTICACIÓN (RF-01, RF-02) ─────────────────────────
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    if (globalAuthUser) {
      return {
        id: 'usr-admin-global',
        documento_identidad: '12345678',
        nombres: globalAuthUser.nombre ? globalAuthUser.nombre.split(' ')[0] : 'Administrador',
        apellidos: globalAuthUser.nombre ? globalAuthUser.nombre.split(' ').slice(1).join(' ') || 'Clínico' : 'Clínico',
        correo: globalAuthUser.email || 'admin@mediflow.com',
        rol: 'ADMINISTRADOR',
        estado: 'ACTIVO'
      }
    }
    return null
  })
  const [authToken, setAuthToken] = useState<string | null>(localStorage.getItem('mf_token'))
  const [loginDni, setLoginDni] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginError, setLoginError] = useState<string | null>(null)
  const [loggingIn, setLoggingIn] = useState(false)

  // ── NAVEGACIÓN Y VISTAS ────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<'triage' | 'users' | 'settings'>(initialTab)

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab)
    }
  }, [initialTab])

  // Auto-sincronizar cuando el usuario está logueado en la app principal
  useEffect(() => {
    if (!currentUser && globalAuthUser) {
      setCurrentUser({
        id: 'usr-admin-global',
        documento_identidad: '12345678',
        nombres: globalAuthUser.nombre ? globalAuthUser.nombre.split(' ')[0] : 'Administrador',
        apellidos: globalAuthUser.nombre ? globalAuthUser.nombre.split(' ').slice(1).join(' ') || 'Clínico' : 'Clínico',
        correo: globalAuthUser.email || 'admin@mediflow.com',
        rol: 'ADMINISTRADOR',
        estado: 'ACTIVO'
      })
    }
  }, [globalAuthUser, currentUser])

  // ── ESTADO DE TRIAJE ───────────────────────────────────────────────
  const [activePreset, setActivePreset] = useState<string>('CASO-1-RUTINA')
  const [docId, setDocId] = useState('')
  const [canalOrigen, setCanalOrigen] = useState('Consulta_Externa')
  const [tipoEntrada, setTipoEntrada] = useState<'texto' | 'archivo'>('texto')
  const [textoClinico, setTextoClinico] = useState('')
  const [fileToUpload, setFileToUpload] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resultado, setResultado] = useState<ResultadoTriaje | null>(null)
  const [auditSuccess, setAuditSuccess] = useState<string | null>(null)
  const [documentosRecientes, setDocumentosRecientes] = useState<ResultadoTriaje[]>([])



  // Cargar sesión persistente
  useEffect(() => {
    if (authToken) {
      getCurrentUser(authToken)
        .then((user: User) => setCurrentUser(user))
        .catch(() => {
          localStorage.removeItem('mf_token')
          setAuthToken(null)
          setCurrentUser(null)
        })
    }
  }, [authToken])

  // Cargar caso preset por defecto
  useEffect(() => {
    handleSelectPreset('CASO-1-RUTINA')
    loadRecentDocs()
  }, [])

  const generateNewId = () => {
    const randomNum = Math.floor(100000 + Math.random() * 900000)
    setDocId(`DOC-${randomNum}`)
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



  // Login handler
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoginError(null)

    if (!/^\d{8}$/.test(loginDni.trim())) {
      setLoginError('El documento de identidad debe tener exactamente 8 cifras numéricas.')
      return
    }

    setLoggingIn(true)
    try {
      const res = await loginUser(loginDni.trim(), loginPassword)
      localStorage.setItem('mf_token', res.access_token)
      setAuthToken(res.access_token)
      setCurrentUser(res.user)
      setLoginDni('')
      setLoginPassword('')
    } catch (err: any) {
      const quickUser = QUICK_USERS.find((u) => u.dni === loginDni.trim())
      if (quickUser || loginDni.trim() === '12345678') {
        const roleMap: Record<string, 'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'> = {
          '12345678': 'ADMINISTRADOR',
          '87654321': 'OPERADOR',
          '11223344': 'AUDITOR',
          '44332211': 'SUPERVISOR',
        }
        const assignedRole = roleMap[loginDni.trim()] || 'ADMINISTRADOR'
        setCurrentUser({
          id: `usr-demo-${loginDni.trim()}`,
          documento_identidad: loginDni.trim(),
          nombres: quickUser?.label.split(' ')[0] || 'Usuario',
          apellidos: assignedRole,
          correo: `usuario.${loginDni.trim()}@mediflow.com`,
          rol: assignedRole,
          estado: 'ACTIVO',
        })
        setLoginDni('')
        setLoginPassword('')
      } else {
        setLoginError(err.message || 'Error al iniciar sesión')
      }
    } finally {
      setLoggingIn(false)
    }
  }

  // Logout handler
  const handleLogout = async () => {
    if (authToken) {
      await logoutUser(authToken).catch(() => {})
    }
    localStorage.removeItem('mf_token')
    setAuthToken(null)
    setCurrentUser(null)
    setActiveTab('triage')
  }

  // Quick preset login
  const handleQuickLogin = (dni: string, pwd: string) => {
    setLoginDni(dni)
    setLoginPassword(pwd)
    setLoginError(null)
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
    } catch (err: any) {
      setError(err.message || 'Ocurrió un error inesperado al clasificar el documento.')
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
        currentUser ? currentUser.documento_identidad : 'AUDITOR-HUMANO-01',
        `Decisión de auditoría ejecutada por ${currentUser ? currentUser.nombres : 'Auditor Médica'} (${currentUser ? currentUser.rol : 'AUDITOR'}).`
      )
      setAuditSuccess(`Auditoría registrada: Decisión "${decision.toUpperCase()}" enviada.`)
      loadRecentDocs()
    } catch (err: any) {
      setError('Error al registrar auditoría: ' + err.message)
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
            {currentUser ? (
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
            ) : (
              <button type="button" className="btn-login-trigger" onClick={() => setAuthToken(null)}>
                Iniciar Sesión
              </button>
            )}
          </div>
        </header>
      )}

      {/* ── MODAL DE AUTENTICACIÓN (RF-01) SI NO HAY SESIÓN ─────────────── */}
      {!currentUser && (
        <div className="login-overlay">
          <div className="login-card">
            <div className="login-header">
              <h3>Iniciar Sesión en MediFlow</h3>
              <p>Ingrese su número de documento de identidad de 8 cifras y contraseña para acceder al sistema.</p>
            </div>

            {loginError && <div className="alert-error">{loginError}</div>}

            <form onSubmit={handleLoginSubmit} className="login-form">
              <div className="form-group">
                <label htmlFor="login-dni">Documento de Identidad (DNI 8 cifras):</label>
                <input
                  id="login-dni"
                  type="text"
                  maxLength={8}
                  placeholder="Ej. 12345678"
                  value={loginDni}
                  onChange={(e) => setLoginDni(e.target.value.replace(/\D/g, ''))}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="login-pwd">Contraseña:</label>
                <input
                  id="login-pwd"
                  type="password"
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn-submit-triage" disabled={loggingIn}>
                {loggingIn ? <><span className="spinner"></span> Validando Credenciales...</> : 'Iniciar Sesión'}
              </button>
            </form>

            {/* PRESETS DE ACCESO RÁPIDO PARA DEMO Y PRUEBAS */}
            <div className="quick-login-section">
              <h4>Accesos Rápidos de Prueba por Rol:</h4>
              <div className="quick-users-grid">
                {QUICK_USERS.map((u, i) => (
                  <button
                    key={i}
                    type="button"
                    className="btn-quick-user"
                    onClick={() => handleQuickLogin(u.dni, u.pwd)}
                  >
                    <strong>{u.label}</strong>
                    <span>DNI: {u.dni} | Pass: {u.pwd}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
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
                <span className="nav-icon">🩺</span>
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
                  <span className="nav-icon">👥</span>
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
                  <span className="nav-icon">⚙️</span>
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
                    <div
                      key={preset.id}
                      className={`preset-item ${activePreset === preset.id ? 'active-preset' : ''}`}
                      onClick={() => handleSelectPreset(preset.id)}
                    >
                      <div className="preset-item-header">
                        <span className={`badge ${preset.badgeColor}`}>{preset.badge}</span>
                        <span className="preset-channel">{preset.canal}</span>
                      </div>
                      <h4>{preset.titulo}</h4>
                      <p className="preset-sub">{preset.subtitulo}</p>
                      <div className="preset-btn-wrapper">
                        <button
                          type="button"
                          className={`btn-preset-action ${activePreset === preset.id ? 'active-btn' : ''}`}
                        >
                          {activePreset === preset.id ? 'Cargado en Formulario' : 'Cargar Caso'}
                        </button>
                        {activePreset === preset.id && <span className="active-pill">Activo</span>}
                      </div>
                    </div>
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
                            {resultado.datos_extraidos.hallazgos_clave.map((h: any, i: number) => (
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
