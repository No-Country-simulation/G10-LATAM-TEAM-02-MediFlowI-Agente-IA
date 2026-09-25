import { useState, useEffect } from 'react'
import {
  obtenerConfiguracion,
  actualizarConfiguracion,
  type ConfiguracionSistema,
} from '../api/triage.api'
import { useAuth } from '../hooks/useAuth'
import { FaSlidersH, FaDatabase, FaCloud, FaSave, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa'
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
      setSettingsSuccess(`Modo de almacenamiento actualizado a ${updated.storage_mode} en PostgreSQL.`)
    } catch (err: any) {
      setSettingsError(err?.message || 'Error al guardar la preferencia en base de datos.')
    } finally {
      setSavingSettings(false)
    }
  }

  if (!canManageSettings) {
    return (
      <div className="container-fluid py-4 px-4 text-center">
        <div className="alert alert-danger rounded-4 p-4 shadow-sm max-w-xl mx-auto">
          <h5 className="fw-bold">Acceso Restringido (RBAC: RF-05)</h5>
          <p className="mb-0">No posee el rol de ADMINISTRADOR necesario para modificar la configuración de almacenamiento.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container-fluid py-4 px-4">
      <div className="card border-0 shadow-sm rounded-4 bg-white p-4 max-w-4xl mx-auto">
        <div className="border-bottom pb-3 mb-4 d-flex align-items-center justify-content-between flex-wrap gap-2">
          <div>
            <h3 className="fw-bold text-dark mb-1 d-flex align-items-center gap-2">
              <FaSlidersH className="text-primary" /> Configuración de Almacenamiento de Documentos
            </h3>
            <span className="text-muted small">
              Preferencia guardada en BD PostgreSQL (<code>configuracion_sistema</code>)
            </span>
          </div>
          <span className="badge bg-primary bg-opacity-10 text-primary px-3 py-2 rounded-pill fw-semibold">
            RF-06 Almacenamiento Híbrido
          </span>
        </div>

        <p className="text-secondary leading-relaxed mb-4">
          Seleccione dónde se almacenarán físicamente los archivos PDF e imágenes clínicas. Los metadatos, resultados de triaje, estados y registros de auditoría continuarán almacenándose siempre en la base de datos PostgreSQL (<code>mediflow_dev</code>).
        </p>

        {settingsSuccess && (
          <div className="alert alert-success rounded-3 mb-4 d-flex align-items-center gap-2">
            <FaCheckCircle className="fs-5" /> {settingsSuccess}
          </div>
        )}
        {settingsError && (
          <div className="alert alert-danger rounded-3 mb-4 d-flex align-items-center gap-2">
            <FaExclamationTriangle className="fs-5" /> {settingsError}
          </div>
        )}

        <div className="row g-4 mb-4">
          {/* OPCIÓN LOCAL */}
          <div className="col-12 col-md-6">
            <div
              className={`card h-100 p-4 rounded-4 cursor-pointer transition-all border-2 ${
                selectedStorageMode === 'LOCAL' ? 'border-primary bg-primary bg-opacity-10 shadow' : 'border-light-subtle bg-light'
              }`}
              onClick={() => {
                setSelectedStorageMode('LOCAL')
                setSettingsError(null)
              }}
              style={{ cursor: 'pointer' }}
            >
              <div className="form-check d-flex align-items-center gap-3 mb-3">
                <input
                  type="radio"
                  id="mode-local"
                  name="storageMode"
                  className="form-check-input fs-5"
                  value="LOCAL"
                  checked={selectedStorageMode === 'LOCAL'}
                  onChange={() => {
                    setSelectedStorageMode('LOCAL')
                    setSettingsError(null)
                  }}
                />
                <label htmlFor="mode-local" className="form-check-label fw-bold fs-5 text-dark cursor-pointer">
                  <FaDatabase className="me-2 text-primary" /> Almacenamiento Local
                </label>
              </div>
              <p className="text-muted small mb-3">
                Los documentos PDF e imágenes se almacenarán físicamente en el disco local del servidor backend.
              </p>
              <div className="bg-white p-2.5 rounded-3 border mb-3">
                <span className="small text-muted d-block">Ruta del Servidor:</span>
                <code className="text-primary fw-semibold small">backend/storage/documentos/</code>
              </div>
              <span className="badge bg-success bg-opacity-10 text-success px-3 py-1.5 rounded-pill fw-semibold w-fit">
                ● Disponible por defecto
              </span>
            </div>
          </div>

          {/* OPCIÓN OCI */}
          <div className="col-12 col-md-6">
            <div
              className={`card h-100 p-4 rounded-4 cursor-pointer transition-all border-2 ${
                selectedStorageMode === 'OCI' ? 'border-primary bg-primary bg-opacity-10 shadow' : 'border-light-subtle bg-light'
              }`}
              onClick={() => {
                setSelectedStorageMode('OCI')
                setSettingsError(null)
              }}
              style={{ cursor: 'pointer' }}
            >
              <div className="form-check d-flex align-items-center gap-3 mb-3">
                <input
                  type="radio"
                  id="mode-oci"
                  name="storageMode"
                  className="form-check-input fs-5"
                  value="OCI"
                  checked={selectedStorageMode === 'OCI'}
                  onChange={() => {
                    setSelectedStorageMode('OCI')
                    setSettingsError(null)
                  }}
                />
                <label htmlFor="mode-oci" className="form-check-label fw-bold fs-5 text-dark cursor-pointer">
                  <FaCloud className="me-2 text-info" /> OCI Object Storage
                </label>
              </div>
              <p className="text-muted small mb-3">
                Los documentos PDF e imágenes se almacenarán físicamente en el servicio de almacenamiento de objetos de Oracle Cloud.
              </p>
              <div className="bg-white p-2.5 rounded-3 border mb-3">
                <span className="small text-muted d-block">Bucket OCI:</span>
                <code className="text-info fw-semibold small">mediflow-documentos-clinicos</code>
              </div>
              {configSys?.oci_configured ? (
                <span className="badge bg-success bg-opacity-10 text-success px-3 py-1.5 rounded-pill fw-semibold w-fit">
                  ✓ Credenciales OCI Configuradas
                </span>
              ) : (
                <span className="badge bg-warning bg-opacity-10 text-warning px-3 py-1.5 rounded-pill fw-semibold w-fit">
                  ⚠ Credenciales OCI No Configuradas (.env)
                </span>
              )}
            </div>
          </div>
        </div>

        {selectedStorageMode === 'OCI' && configSys && !configSys.oci_configured && (
          <div className="alert alert-warning rounded-3 mb-4 d-flex align-items-center gap-2">
            <FaExclamationTriangle className="fs-5 text-warning flex-shrink-0" />
            <div>
              <strong>Advertencia OCI:</strong> Las variables de entorno de Oracle Cloud no están configuradas en el archivo <code>.env</code>.
            </div>
          </div>
        )}

        <div className="d-flex justify-content-end border-top pt-3 mt-2">
          <button
            type="button"
            className="btn btn-primary px-4 py-2.5 fw-bold rounded-pill shadow-sm d-flex align-items-center gap-2"
            disabled={savingSettings}
            onClick={handleSaveSettings}
          >
            {savingSettings ? (
              <><span className="spinner"></span> Guardando en Base de Datos...</>
            ) : (
              <><FaSave /> Guardar Preferencia en Base de Datos</>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
