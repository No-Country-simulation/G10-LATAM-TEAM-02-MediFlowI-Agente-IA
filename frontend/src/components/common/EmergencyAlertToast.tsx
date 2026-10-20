import { Link } from 'react-router-dom'
import { FaExclamationTriangle, FaTimes, FaVolumeUp, FaVolumeMute, FaExternalLinkAlt } from 'react-icons/fa'
import type { AlertaGuardia } from '../../services/alertStreamService'

interface EmergencyAlertToastProps {
  alerts: AlertaGuardia[]
  onDismiss: (id: string) => void
  soundEnabled: boolean
  onToggleSound: () => void
}

export default function EmergencyAlertToast({
  alerts,
  onDismiss,
  soundEnabled,
  onToggleSound,
}: EmergencyAlertToastProps) {
  if (alerts.length === 0) return null

  return (
    <div
      role="region"
      aria-label="Alertas críticas de guardia"
      className="fixed top-4 inset-x-3 sm:inset-x-auto sm:right-4 z-50 flex flex-col gap-3 sm:max-w-[420px] pointer-events-auto"
    >
      {/* Barra superior de control de sonido */}
      <div className="flex justify-end items-center px-1">
        <button
          type="button"
          onClick={onToggleSound}
          title={soundEnabled ? 'Silenciar alertas acústicas' : 'Activar sonido de alerta'}
          className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 bg-white/90 hover:bg-white text-slate-700 rounded-full shadow-xs border border-slate-200 transition-colors cursor-pointer"
        >
          {soundEnabled ? (
            <>
              <FaVolumeUp className="text-red-600" />
              <span>Sonido activado</span>
            </>
          ) : (
            <>
              <FaVolumeMute className="text-slate-400" />
              <span>Sonido silenciado</span>
            </>
          )}
        </button>
      </div>

      {alerts.map((alert) => (
        <div
          key={alert.id}
          role="alert"
          className="bg-red-50/95 border-2 border-red-500 rounded-2xl p-4 shadow-xl backdrop-blur-sm transition-all duration-300 animate-in fade-in slide-in-from-top-4"
        >
          <div className="flex items-start gap-3">
            <div className="p-2.5 bg-red-600 text-white rounded-xl shadow-xs shrink-0 animate-pulse">
              <FaExclamationTriangle size={18} />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-bold text-xs uppercase tracking-wider text-red-700 bg-red-100 px-2 py-0.5 rounded-full">
                  Emergencia Médica
                </span>
                <button
                  type="button"
                  onClick={() => onDismiss(alert.id)}
                  aria-label="Descartar alerta"
                  className="text-slate-400 hover:text-red-700 p-1 rounded-lg transition-colors cursor-pointer"
                >
                  <FaTimes size={14} />
                </button>
              </div>

              <h4 className="font-bold text-sm text-slate-900 truncate" title={alert.documento_id}>
                Doc: {alert.documento_id}
              </h4>
              <p className="text-xs text-slate-700 mt-1 line-clamp-2 leading-relaxed">
                {alert.mensaje || 'Caso crítico clasificado en Cola de Emergencia Médica.'}
              </p>

              <div className="mt-3 flex items-center justify-between pt-2 border-t border-red-200/60">
                <span className="text-[11px] text-slate-500 font-medium">
                  {new Date(alert.fecha).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
                <Link
                  to={`/documentos/${encodeURIComponent(alert.documento_id)}`}
                  onClick={() => onDismiss(alert.id)}
                  className="inline-flex items-center gap-1 text-xs font-bold text-red-700 hover:text-red-800 hover:underline"
                >
                  <span>Atender caso</span>
                  <FaExternalLinkAlt size={11} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
