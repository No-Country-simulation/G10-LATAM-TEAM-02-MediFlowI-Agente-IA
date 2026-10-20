import { useCallback, useState, useEffect } from 'react'
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
  FaDatabase,
} from 'react-icons/fa'

export default function StorageSettingsView() {
  const { user: currentUser } = useAuth()
  const [configSys, setConfigSys] = useState<ConfiguracionSistema | null>(null)
  const [selectedStorageMode, setSelectedStorageMode] = useState<'LOCAL' | 'OCI'>('LOCAL')
  const [savingSettings, setSavingSettings] = useState(false)
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)

  const canManageSettings = Boolean(currentUser && currentUser.rol === 'ADMINISTRADOR')

  const loadSettings = useCallback(async () => {
    try {
      const cfg = await obtenerConfiguracion()
      setConfigSys(cfg)
      setSelectedStorageMode(cfg.storage_mode)
    } catch (err) {
      setSettingsError(
        err instanceof Error
          ? err.message
          : 'No se pudo conectar con el servicio de configuración.'
      )
    }
  }, [])

  useEffect(() => {
    queueMicrotask(() => void loadSettings())
  }, [loadSettings])

  const handleSaveSettings = async () => {
    setSavingSettings(true)
    setSettingsSuccess(null)
    setSettingsError(null)

    try {
      const updated = await actualizarConfiguracion(selectedStorageMode)
      setConfigSys(updated)
      setSelectedStorageMode(updated.storage_mode)
      setSettingsSuccess(`Preferencia guardada: Almacenamiento ${updated.storage_mode} actualizado en PostgreSQL.`)
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : 'Error al guardar la preferencia en la base de datos.')
    } finally {
      setSavingSettings(false)
    }
  }

  if (!canManageSettings) {
    return (
      <div className="clinical-page text-center py-8">
        <div className="bg-rose-50 border border-rose-200 rounded-3xl p-6 shadow-2xs max-w-xl mx-auto text-rose-800">
          <div className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 mx-auto mb-3">
            <FaExclamationTriangle size={22} />
          </div>
          <h5 className="font-bold text-lg mb-1">Acceso Restringido (RBAC)</h5>
          <p className="text-sm text-rose-700 mb-0">
            No posee el rol de ADMINISTRADOR necesario para modificar la configuración de almacenamiento.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="clinical-page w-full max-w-5xl mx-auto">
      {/* CABECERA ESTÁNDAR DEL SISTEMA (Consistente con todo MediFlow) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-bold text-sky-700 uppercase tracking-wider bg-sky-50 border border-sky-200/80 px-2.5 py-0.5 rounded-full inline-flex items-center gap-1">
              <FaSlidersH size={10} /> Sistema / Configuración
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2041] tracking-tight mb-1">
            Configuración de Almacenamiento
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 font-medium mb-0">
            Defina la ubicación física de almacenamiento para archivos clínicos (PDFs e Imágenes)
          </p>
        </div>

        <div className="inline-flex items-center gap-2 self-start sm:self-center bg-slate-50 border border-slate-200 px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-700 shadow-2xs">
          <FaDatabase className="text-sky-600" />
          <span>PostgreSQL Sync</span>
        </div>
      </div>

      {/* CONTENEDOR PRINCIPAL CLÍNICO */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-2xs p-5 sm:p-7">
        {/* NOTA DE FUENTE ÚNICA DE VERDAD */}
        <div className="bg-sky-50/70 border border-sky-200/80 rounded-2xl p-4 mb-6 flex items-start gap-3.5 text-sky-950">
          <div className="w-8 h-8 rounded-xl bg-sky-100 flex items-center justify-center text-sky-700 shrink-0 mt-0.5">
            <FaInfoCircle size={16} />
          </div>
          <div className="text-xs sm:text-sm leading-relaxed">
            <strong className="block font-bold text-sky-900 mb-0.5 text-sm sm:text-base">
              Fuente Única de Verdad: PostgreSQL
            </strong>
            Los metadatos, resultados del triaje, diagnósticos CIE-10 y la trazabilidad médica se guardan siempre en la base de datos{' '}
            <strong className="font-semibold text-sky-950">PostgreSQL (mediflow_dev)</strong>. La opción seleccionada a continuación únicamente determina dónde se depositan los archivos adjuntos.
          </div>
        </div>

        {/* MENSAJES DE ESTADO */}
        {settingsSuccess && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-3.5 mb-5 flex items-center gap-2.5 text-emerald-800 text-xs sm:text-sm shadow-2xs">
            <FaCheckCircle className="text-emerald-600 shrink-0 text-base" />
            <span>{settingsSuccess}</span>
          </div>
        )}
        {settingsError && (
          <div className="bg-rose-50 border border-rose-200 rounded-2xl p-3.5 mb-5 flex items-center gap-2.5 text-rose-800 text-xs sm:text-sm shadow-2xs">
            <FaExclamationTriangle className="text-rose-600 shrink-0 text-base" />
            <span>{settingsError}</span>
          </div>
        )}

        {/* TARJETAS DE SELECCIÓN DE ALMACENAMIENTO */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          {/* OPCIÓN 1: LOCAL */}
          <div
            className={`rounded-2xl p-5 sm:p-6 transition-all cursor-pointer flex flex-col justify-between ${
              selectedStorageMode === 'LOCAL'
                ? 'border-2 border-[#204A79] bg-sky-50/30 shadow-xs ring-4 ring-[#204A79]/5'
                : 'border border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs'
            }`}
            onClick={() => {
              setSelectedStorageMode('LOCAL')
              setSettingsError(null)
            }}
          >
            <div>
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-11 h-11 rounded-2xl flex items-center justify-center transition-colors shrink-0 ${
                      selectedStorageMode === 'LOCAL' ? 'bg-[#204A79] text-white shadow-xs' : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    <FaHdd size={18} />
                  </div>
                  <div>
                    <h5 className="font-bold text-slate-900 text-sm sm:text-base mb-0">Almacenamiento Local</h5>
                    <span className="text-xs text-slate-500 font-medium">Servidor Backend</span>
                  </div>
                </div>

                {selectedStorageMode === 'LOCAL' && (
                  <span className="bg-[#204A79] text-white text-[11px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1 shadow-2xs">
                    <FaCheck size={10} /> Activo
                  </span>
                )}
              </div>

              <p className="text-xs sm:text-sm text-slate-600 mb-4 leading-relaxed">
                Los documentos PDF e imágenes se almacenan físicamente en el volumen de disco local asignado al servidor backend.
              </p>

              <div className="bg-slate-50 border border-slate-200/80 p-3 rounded-xl mb-4">
                <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Ruta Física Servidor:</span>
                <code className="text-[#204A79] font-mono font-bold text-xs">backend/storage/documentos/</code>
              </div>
            </div>

            <div className="pt-2">
              <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
                ● Disponible por defecto
              </span>
            </div>
          </div>

          {/* OPCIÓN 2: OCI OBJECT STORAGE */}
          <div
            className={`rounded-2xl p-5 sm:p-6 transition-all cursor-pointer flex flex-col justify-between ${
              selectedStorageMode === 'OCI'
                ? 'border-2 border-[#204A79] bg-sky-50/30 shadow-xs ring-4 ring-[#204A79]/5'
                : 'border border-slate-200 bg-white hover:border-slate-300 hover:shadow-2xs'
            }`}
            onClick={() => {
              setSelectedStorageMode('OCI')
              setSettingsError(null)
            }}
          >
            <div>
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-11 h-11 rounded-2xl flex items-center justify-center transition-colors shrink-0 ${
                      selectedStorageMode === 'OCI' ? 'bg-[#204A79] text-white shadow-xs' : 'bg-sky-50 text-sky-700'
                    }`}
                  >
                    <FaCloud size={20} />
                  </div>
                  <div>
                    <h5 className="font-bold text-slate-900 text-sm sm:text-base mb-0">OCI Object Storage</h5>
                    <span className="text-xs text-slate-500 font-medium">Oracle Cloud Infrastructure</span>
                  </div>
                </div>

                {selectedStorageMode === 'OCI' && (
                  <span className="bg-[#204A79] text-white text-[11px] font-bold px-2.5 py-1 rounded-full flex items-center gap-1 shadow-2xs">
                    <FaCheck size={10} /> Activo
                  </span>
                )}
              </div>

              <p className="text-xs sm:text-sm text-slate-600 mb-4 leading-relaxed">
                Los documentos PDF e imágenes se persisten en el servicio seguro de almacenamiento de objetos de Oracle Cloud.
              </p>

              <div className="bg-slate-50 border border-slate-200/80 p-3 rounded-xl mb-4">
                <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Bucket OCI Configurado:</span>
                <code className="text-sky-700 font-mono font-bold text-xs">mediflow-documentos-clinicos</code>
              </div>
            </div>

            <div className="pt-2">
              {configSys?.oci_configured ? (
                <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
                  ✓ Credenciales OCI listas (.env)
                </span>
              ) : (
                <span className="inline-flex items-center text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full">
                  ⚠ Credenciales OCI no detectadas
                </span>
              )}
            </div>
          </div>
        </div>

        {selectedStorageMode === 'OCI' && configSys && !configSys.oci_configured && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-6 flex items-start gap-3 text-amber-900 text-xs sm:text-sm">
            <FaExclamationTriangle className="text-amber-600 shrink-0 text-base mt-0.5" />
            <div>
              <strong className="font-bold">Atención:</strong> Las variables de entorno para Oracle Cloud no están configuradas en el archivo <code className="bg-amber-100 px-1.5 py-0.5 rounded text-amber-900 font-mono text-xs">.env</code>. Se recomienda mantener el modo <strong>LOCAL</strong> mientras no se suministren las claves de acceso.
            </div>
          </div>
        )}

        {/* BOTÓN GUARDAR PREFERENCIA */}
        <div className="flex items-center justify-end border-t border-slate-100 pt-5 mt-2">
          <button
            type="button"
            className="px-6 py-2.5 rounded-xl bg-[#204A79] hover:bg-[#153457] text-white text-xs sm:text-sm font-semibold transition-colors shadow-xs flex items-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
            disabled={savingSettings}
            onClick={handleSaveSettings}
          >
            {savingSettings ? (
              <>
                <div className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
                <span>Guardando en PostgreSQL...</span>
              </>
            ) : (
              <>
                <FaSave size={14} />
                <span>Guardar Preferencia en Base de Datos</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
