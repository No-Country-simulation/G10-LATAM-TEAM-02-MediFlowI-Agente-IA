import { useState, useEffect } from 'react'
import {
  obtenerConfiguracion,
  actualizarConfiguracion,
  type ConfiguracionSistema,
} from '../api/triage.api'
import { useAuth } from '../hooks/useAuth'
import {
  FaSlidersH,
  FaCloud,
  FaSave,
  FaCheckCircle,
  FaExclamationTriangle,
  FaCheck,
  FaInfoCircle,
  FaHdd,
} from 'react-icons/fa'
import '../App.css'

export default function StorageSettingsView() {
  const { user: currentUser } = useAuth()
  const [configSys, setConfigSys] = useState<ConfiguracionSistema | null>(null)
  const [selectedStorageMode, setSelectedStorageMode] = useState<'LOCAL' | 'OCI'>('LOCAL')
  const [savingSettings, setSavingSettings] = useState(false)
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)

  const canManageSettings =
    !currentUser ||
    currentUser.rol === 'ADMINISTRADOR' ||
    currentUser.rol === 'ADMIN' ||
    currentUser.username === 'admin'

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const cfg = await obtenerConfiguracion()
      setConfigSys(cfg)
      setSelectedStorageMode(cfg.storage_mode)
    } catch {
      // Fallback
    }
  }

  const handleSaveSettings = async () => {
    setSavingSettings(true)
    setSettingsSuccess(null)
    setSettingsError(null)

    try {
      const updated = await actualizarConfiguracion(selectedStorageMode)
      setConfigSys(updated)
      setSelectedStorageMode(updated.storage_mode)
      setSettingsSuccess(`Preferencia guardada: Almacenamiento ${updated.storage_mode} actualizado en PostgreSQL.`)
    } catch (err: any) {
      setSettingsError(err?.message || 'Error al guardar la preferencia en la base de datos.')
    } finally {
      setSavingSettings(false)
    }
  }

  if (!canManageSettings) {
    return (
      <div className="container-fluid py-4 px-4 text-center">
        <div className="alert alert-danger rounded-4 p-4 shadow-sm max-w-xl mx-auto">
          <h5 className="fw-bold">Acceso Restringido (RBAC)</h5>
          <p className="mb-0">No posee el rol de ADMINISTRADOR necesario para modificar la configuración de almacenamiento.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container-fluid py-4 px-4">
      <div className="card border-0 shadow-lg rounded-4 overflow-hidden bg-white max-w-4xl mx-auto">
        {/* CABECERA CON GRADIENTE INSTITUCIONAL */}
        <div
          className="p-4 text-white position-relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)',
          }}
        >
          <div className="d-flex align-items-center justify-content-between position-relative" style={{ zIndex: 2 }}>
            <div className="d-flex align-items-center gap-3">
              <div
                className="bg-white bg-opacity-20 text-white p-3 rounded-3 d-flex align-items-center justify-content-center shadow-sm"
                style={{ backdropFilter: 'blur(8px)', width: '48px', height: '48px' }}
              >
                <FaSlidersH className="fs-4" />
              </div>
              <div>
                <h4 className="fw-bold mb-1 text-white">Configuración de Almacenamiento</h4>
                <p className="mb-0 text-white-50 small">
                  Defina la ubicación física de almacenamiento para archivos clínicos (PDFs e Imágenes)
                </p>
              </div>
            </div>
            <span className="badge bg-white bg-opacity-20 text-white px-3 py-2 rounded-pill fw-semibold border border-white border-opacity-25">
              PostgreSQL Sync
            </span>
          </div>
        </div>

        {/* CONTENIDO PRINCIPAL */}
        <div className="p-4">
          {/* NOTA DE FUENTE ÚNICA DE VERDAD */}
          <div className="alert alert-info border-0 shadow-sm rounded-4 p-3 mb-4 d-flex align-items-start gap-3 bg-primary bg-opacity-10 text-primary">
            <FaInfoCircle className="fs-4 flex-shrink-0 mt-0.5" />
            <div className="small">
              <strong className="d-block mb-1 text-dark fs-6">Fuente Única de Verdad: PostgreSQL</strong>
              Los metadatos, resultados del triaje, diagnósticos CIE-10 y la trazabilidad médica se guardan siempre en la base de datos <strong>PostgreSQL (mediflow_dev)</strong>. La opción seleccionada a continuación únicamente determina dónde se depositan los archivos adjuntos.
            </div>
          </div>

          {settingsSuccess && (
            <div className="alert alert-success border-0 shadow-sm rounded-3 mb-4 d-flex align-items-center gap-2">
              <FaCheckCircle className="fs-5" /> {settingsSuccess}
            </div>
          )}
          {settingsError && (
            <div className="alert alert-danger border-0 shadow-sm rounded-3 mb-4 d-flex align-items-center gap-2">
              <FaExclamationTriangle className="fs-5" /> {settingsError}
            </div>
          )}

          {/* TARJETAS DE SELECCIÓN DE ALMACENAMIENTO */}
          <div className="row g-4 mb-4">
            {/* OPCIÓN 1: LOCAL */}
            <div className="col-12 col-md-6">
              <div
                className={`card h-100 p-4 border transition-all rounded-4 position-relative ${
                  selectedStorageMode === 'LOCAL'
                    ? 'border-primary bg-primary bg-opacity-10 shadow-sm'
                    : 'border-light-subtle bg-light hover-shadow'
                }`}
                style={{
                  cursor: 'pointer',
                  borderWidth: selectedStorageMode === 'LOCAL' ? '2px' : '1px',
                  transition: 'all 0.2s ease-in-out',
                }}
                onClick={() => {
                  setSelectedStorageMode('LOCAL')
                  setSettingsError(null)
                }}
              >
                <div className="d-flex align-items-start justify-content-between mb-3">
                  <div className="d-flex align-items-center gap-3">
                    <div
                      className={`p-3 rounded-3 d-flex align-items-center justify-content-center ${
                        selectedStorageMode === 'LOCAL' ? 'bg-primary text-white' : 'bg-white text-primary shadow-sm'
                      }`}
                      style={{ width: '44px', height: '44px' }}
                    >
                      <FaHdd className="fs-4" />
                    </div>
                    <div>
                      <h5 className="fw-bold text-dark mb-0">Almacenamiento Local</h5>
                      <span className="text-muted extra-small" style={{ fontSize: '0.75rem' }}>Servidor Backend</span>
                    </div>
                  </div>
                  {selectedStorageMode === 'LOCAL' && (
                    <span className="badge bg-primary text-white rounded-pill px-2.5 py-1 small d-flex align-items-center gap-1">
                      <FaCheck /> Activo
                    </span>
                  )}
                </div>

                <p className="text-muted small mb-3">
                  Los documentos PDF e imágenes se almacenan físicamente en el volumen de disco local asignado al servidor backend.
                </p>

                <div className="bg-white p-3 rounded-3 border mb-3">
                  <span className="small text-muted d-block fw-semibold mb-1">Ruta Física Servidor:</span>
                  <code className="text-primary fw-bold small">backend/storage/documentos/</code>
                </div>

                <div className="mt-auto">
                  <span className="badge bg-success-subtle text-success border border-success-subtle px-3 py-1.5 rounded-pill fw-semibold">
                    ● Disponible por defecto
                  </span>
                </div>
              </div>
            </div>

            {/* OPCIÓN 2: OCI OBJECT STORAGE */}
            <div className="col-12 col-md-6">
              <div
                className={`card h-100 p-4 border transition-all rounded-4 position-relative ${
                  selectedStorageMode === 'OCI'
                    ? 'border-primary bg-primary bg-opacity-10 shadow-sm'
                    : 'border-light-subtle bg-light hover-shadow'
                }`}
                style={{
                  cursor: 'pointer',
                  borderWidth: selectedStorageMode === 'OCI' ? '2px' : '1px',
                  transition: 'all 0.2s ease-in-out',
                }}
                onClick={() => {
                  setSelectedStorageMode('OCI')
                  setSettingsError(null)
                }}
              >
                <div className="d-flex align-items-start justify-content-between mb-3">
                  <div className="d-flex align-items-center gap-3">
                    <div
                      className={`p-3 rounded-3 d-flex align-items-center justify-content-center ${
                        selectedStorageMode === 'OCI' ? 'bg-primary text-white' : 'bg-white text-info shadow-sm'
                      }`}
                      style={{ width: '44px', height: '44px' }}
                    >
                      <FaCloud className="fs-4" />
                    </div>
                    <div>
                      <h5 className="fw-bold text-dark mb-0">OCI Object Storage</h5>
                      <span className="text-muted extra-small" style={{ fontSize: '0.75rem' }}>Oracle Cloud Infrastructure</span>
                    </div>
                  </div>
                  {selectedStorageMode === 'OCI' && (
                    <span className="badge bg-primary text-white rounded-pill px-2.5 py-1 small d-flex align-items-center gap-1">
                      <FaCheck /> Activo
                    </span>
                  )}
                </div>

                <p className="text-muted small mb-3">
                  Los documentos PDF e imágenes se persisten en el servicio seguro de almacenamiento de objetos de Oracle Cloud.
                </p>

                <div className="bg-white p-3 rounded-3 border mb-3">
                  <span className="small text-muted d-block fw-semibold mb-1">Bucket OCI Configurado:</span>
                  <code className="text-info fw-bold small">mediflow-documentos-clinicos</code>
                </div>

                <div className="mt-auto">
                  {configSys?.oci_configured ? (
                    <span className="badge bg-success-subtle text-success border border-success-subtle px-3 py-1.5 rounded-pill fw-semibold">
                      ✓ Credenciales OCI listas (.env)
                    </span>
                  ) : (
                    <span className="badge bg-warning-subtle text-warning border border-warning-subtle px-3 py-1.5 rounded-pill fw-semibold">
                      ⚠ Credenciales OCI no detectadas
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {selectedStorageMode === 'OCI' && configSys && !configSys.oci_configured && (
            <div className="alert alert-warning border-0 shadow-sm rounded-3 mb-4 d-flex align-items-center gap-2">
              <FaExclamationTriangle className="fs-5 text-warning flex-shrink-0" />
              <div className="small">
                <strong>Atención:</strong> Las variables de entorno para Oracle Cloud no están configuradas en el archivo <code>.env</code>. Se recomienda mantener el modo <strong>LOCAL</strong> mientras no se suministren las claves de acceso.
              </div>
            </div>
          )}

          {/* BOTÓN GUARDAR PREFERENCIA */}
          <div className="d-flex justify-content-end border-top pt-3 mt-4">
            <button
              type="button"
              className="btn btn-primary px-4 py-2.5 fw-bold rounded-pill shadow-sm d-flex align-items-center gap-2"
              disabled={savingSettings}
              onClick={handleSaveSettings}
            >
              {savingSettings ? (
                <>
                  <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando en PostgreSQL...
                </>
              ) : (
                <>
                  <FaSave /> Guardar Preferencia en Base de Datos
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
