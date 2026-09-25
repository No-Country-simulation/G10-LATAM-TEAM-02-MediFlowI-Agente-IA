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
} from '../api/triage.api'
import {
  loginUser,
  logoutUser,
  getCurrentUser,
  fetchUsers,
  createNewUser,
  updateUserDetails,
  type User,
} from '../api/auth.api'
import '../App.css'

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

export default function TriageConsoleView() {
  // ── ESTADO DE AUTENTICACIÓN (RF-01, RF-02) ─────────────────────────
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [authToken, setAuthToken] = useState<string | null>(localStorage.getItem('mf_token'))
  const [loginDni, setLoginDni] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginError, setLoginError] = useState<string | null>(null)
  const [loggingIn, setLoggingIn] = useState(false)

  // ── NAVEGACIÓN Y VISTAS ────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<'triage' | 'users' | 'settings'>('triage')

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

  // ── ESTADO DE CONFIGURACIÓN ────────────────────────────────────────
  const [configSys, setConfigSys] = useState<ConfiguracionSistema | null>(null)
  const [selectedStorageMode, setSelectedStorageMode] = useState<'LOCAL' | 'OCI'>('LOCAL')
  const [savingSettings, setSavingSettings] = useState(false)
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)

  // ── ESTADO DE GESTIÓN DE USUARIOS (RF-03, RF-04) ────────────────────
  const [usersList, setUsersList] = useState<User[]>([])
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [newDni, setNewDni] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newNombres, setNewNombres] = useState('')
  const [newApellidos, setNewApellidos] = useState('')
  const [newCorreo, setNewCorreo] = useState('')
  const [newTelefono, setNewTelefono] = useState('')
  const [newRol, setNewRol] = useState<'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'>('OPERADOR')
  const [userFormError, setUserFormError] = useState<string | null>(null)
  const [userFormSuccess, setUserFormSuccess] = useState<string | null>(null)
  const [savingUser, setSavingUser] = useState(false)

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
    loadSettings()
  }, [])

  // Cargar usuarios cuando se abre la pestaña
  useEffect(() => {
    if (activeTab === 'users' && authToken && currentUser?.rol === 'ADMINISTRADOR') {
      loadUsers()
    }
  }, [activeTab, authToken, currentUser])

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

  const loadSettings = async () => {
    try {
      const cfg = await obtenerConfiguracion()
      setConfigSys(cfg)
      setSelectedStorageMode(cfg.storage_mode)
    } catch (e) {
      console.error('Error cargando configuraciones del sistema:', e)
    }
  }

  const loadUsers = async () => {
    if (!authToken) return
    setLoadingUsers(true)
    try {
      const list = await fetchUsers(authToken)
      setUsersList(list)
    } catch (e: any) {
      console.error(e)
    } finally {
      setLoadingUsers(false)
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
      setLoginError(err.message || 'Error al iniciar sesión')
    } finally {
      setLoggingIn(false)
    }
  }

  // Logout handler
  const handleLogout = async () => {
    if (authToken) {
      await logoutUser(authToken)
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

  // Guardar configuración de almacenamiento
  const handleSaveSettings = async () => {
    setSavingSettings(true)
    setSettingsSuccess(null)
    setSettingsError(null)

    try {
      const updated = await actualizarConfiguracion(selectedStorageMode)
      setConfigSys(updated)
      setSettingsSuccess(`Modo de almacenamiento actualizado a "${selectedStorageMode}" en la base de datos PostgreSQL.`)
    } catch (err: any) {
      setSettingsError(err.message || 'Error al guardar la preferencia de almacenamiento.')
    } finally {
      setSavingSettings(false)
    }
  }

  // Registrar nuevo usuario (RF-03)
  const handleCreateUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!authToken) return
    setUserFormError(null)
    setUserFormSuccess(null)

    if (!/^\d{8}$/.test(newDni.trim())) {
      setUserFormError('El documento de identidad debe contener exactamente 8 cifras.')
      return
    }

    setSavingUser(true)
    try {
      await createNewUser(authToken, {
        documento_identidad: newDni.trim(),
        password: newPassword,
        nombres: newNombres,
        apellidos: newApellidos,
        correo: newCorreo || undefined,
        telefono: newTelefono || undefined,
        rol: newRol,
        estado: 'ACTIVO',
      })
      setUserFormSuccess(`Usuario ${newNombres} ${newApellidos} (DNI ${newDni}) registrado exitosamente con rol ${newRol}.`)
      setNewDni('')
      setNewPassword('')
      setNewNombres('')
      setNewApellidos('')
      setNewCorreo('')
      setNewTelefono('')
      loadUsers()
    } catch (err: any) {
      setUserFormError(err.message || 'Error al registrar usuario')
    } finally {
      setSavingUser(false)
    }
  }

  // Cambiar rol o estado de usuario
  const handleToggleUserStatus = async (user: User) => {
    if (!authToken) return
    const nextStatus = user.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'
    try {
      await updateUserDetails(authToken, user.id, { estado: nextStatus })
      loadUsers()
    } catch (e: any) {
      alert('Error cambiando estado: ' + e.message)
    }
  }

  const handleChangeUserRole = async (user: User, nextRol: any) => {
    if (!authToken) return
    try {
      await updateUserDetails(authToken, user.id, { rol: nextRol })
      loadUsers()
    } catch (e: any) {
      alert('Error cambiando rol: ' + e.message)
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
      {/* ── HEADER PRINCIPAL ────────────────────────────────────────────── */}
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

      {/* ── NAVEGACIÓN NAV TABS RESTRINGIDAS POR ROL (RF-05) ───────────────── */}
      {currentUser && (
        <nav className="nav-tabs">
          <button
            type="button"
            className={`tab-btn ${activeTab === 'triage' ? 'active' : ''}`}
            onClick={() => setActiveTab('triage')}
          >
            Triaje Clínico
          </button>

          {canManageUsers && (
            <button
              type="button"
              className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              Gestión de Usuarios
            </button>
          )}

          {canManageSettings && (
            <button
              type="button"
              className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              Configuración
            </button>
          )}
        </nav>
      )}

      {/* ── CONTENIDO PRINCIPAL DE LA APLICACIÓN ─────────────────────────── */}
      <main className="main-content">
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

        {/* ─────────────────────────────────────────────────────────────────── */}
        {/* VISTA 2: GESTIÓN DE USUARIOS Y ROLES (RF-03, RF-04)                 */}
        {/* ─────────────────────────────────────────────────────────────────── */}
        {activeTab === 'users' && canManageUsers && (
          <div className="users-view">
            <section className="card form-card">
              <div className="card-header">
                <h3>RF-03 — Registrar Nuevo Usuario del Sistema</h3>
              </div>

              {userFormSuccess && <div className="alert-success">{userFormSuccess}</div>}
              {userFormError && <div className="alert-error">{userFormError}</div>}

              <form onSubmit={handleCreateUserSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="u-dni">Documento de Identidad (8 cifras DNI)</label>
                    <input
                      id="u-dni"
                      type="text"
                      maxLength={8}
                      placeholder="Ej. 77665544"
                      value={newDni}
                      onChange={(e) => setNewDni(e.target.value.replace(/\D/g, ''))}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="u-pwd">Contraseña Inicial</label>
                    <input
                      id="u-pwd"
                      type="password"
                      placeholder="••••••••"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="u-nom">Nombres</label>
                    <input
                      id="u-nom"
                      type="text"
                      placeholder="Ej. María Fernanda"
                      value={newNombres}
                      onChange={(e) => setNewNombres(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="u-ape">Apellidos</label>
                    <input
                      id="u-ape"
                      type="text"
                      placeholder="Ej. Gómez Torres"
                      value={newApellidos}
                      onChange={(e) => setNewApellidos(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="u-cor">Correo Electrónico (Opcional)</label>
                    <input
                      id="u-cor"
                      type="email"
                      placeholder="maria.gomez@clinica.com"
                      value={newCorreo}
                      onChange={(e) => setNewCorreo(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="u-rol">Rol del Sistema (RF-04)</label>
                    <select
                      id="u-rol"
                      value={newRol}
                      onChange={(e) => setNewRol(e.target.value as any)}
                    >
                      <option value="OPERADOR">OPERADOR (Registra/Carga Documentos)</option>
                      <option value="AUDITOR">AUDITOR (Revisa Casos HITL / Ambiguos)</option>
                      <option value="SUPERVISOR">SUPERVISOR (Consulta Dashboard & KPI)</option>
                      <option value="ADMINISTRADOR">ADMINISTRADOR (Gestión Completa)</option>
                    </select>
                  </div>
                </div>

                <button type="submit" className="btn-submit-triage" disabled={savingUser}>
                  {savingUser ? <><span className="spinner"></span> Guardando Usuario...</> : 'Registrar Trabajador'}
                </button>
              </form>
            </section>

            {/* TABLA DE USUARIOS REGISTRADOS */}
            <section className="card history-section">
              <div className="card-header">
                <h3>Usuarios Registrados en la Clínica</h3>
                <button type="button" className="btn-secondary" onClick={loadUsers}>
                  Refrescar Lista
                </button>
              </div>

              {loadingUsers ? (
                <div className="loading-state"><span className="spinner"></span> Cargando usuarios...</div>
              ) : (
                <div className="table-wrapper">
                  <table className="docs-table">
                    <thead>
                      <tr>
                        <th>DNI (8 cifras)</th>
                        <th>Nombres y Apellidos</th>
                        <th>Correo</th>
                        <th>Rol Asignado</th>
                        <th>Estado</th>
                        <th>Acción Estado</th>
                        <th>Cambiar Rol</th>
                      </tr>
                    </thead>
                    <tbody>
                      {usersList.map((u) => (
                        <tr key={u.id}>
                          <td><code>{u.documento_identidad}</code></td>
                          <td><strong>{u.nombres} {u.apellidos}</strong></td>
                          <td>{u.correo || 'N/D'}</td>
                          <td>
                            <span className={`role-pill role-${u.rol.toLowerCase()}`}>
                              {u.rol}
                            </span>
                          </td>
                          <td>
                            <span className={`status-indicator ${u.estado === 'ACTIVO' ? 'text-green' : 'text-amber'}`}>
                              {u.estado}
                            </span>
                          </td>
                          <td>
                            <button
                              type="button"
                              className={`btn-action-status ${u.estado === 'ACTIVO' ? 'btn-deactivate' : 'btn-activate'}`}
                              onClick={() => handleToggleUserStatus(u)}
                            >
                              {u.estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}
                            </button>
                          </td>
                          <td>
                            <select
                              value={u.rol}
                              className="select-role-change"
                              onChange={(e) => handleChangeUserRole(u, e.target.value)}
                            >
                              <option value="OPERADOR">OPERADOR</option>
                              <option value="AUDITOR">AUDITOR</option>
                              <option value="SUPERVISOR">SUPERVISOR</option>
                              <option value="ADMINISTRADOR">ADMINISTRADOR</option>
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        )}

        {/* ─────────────────────────────────────────────────────────────────── */}
        {/* VISTA 3: CONFIGURACIÓN DE ALMACENAMIENTO DE DOCUMENTOS             */}
        {/* ─────────────────────────────────────────────────────────────────── */}
        {activeTab === 'settings' && canManageSettings && (
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

              {selectedStorageMode === 'OCI' && configSys && !configSys.oci_configured && (
                <div className="alert-warning">
                  <strong>Advertencia OCI:</strong> Las variables de entorno de Oracle Cloud no están configuradas en el archivo <code>.env</code>.
                </div>
              )}

              <div className="settings-actions">
                <button
                  type="button"
                  className="btn-submit-triage"
                  disabled={savingSettings}
                  onClick={handleSaveSettings}
                >
                  {savingSettings ? <><span className="spinner"></span> Guardando en Base de Datos...</> : <>Guardar Preferencia en Base de Datos</>}
                </button>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}
