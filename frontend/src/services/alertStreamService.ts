/**
 * MediFlow - Servicio de Transmisión de Alertas de Guardia en Tiempo Real (SSE)
 * Consume GET /api/v1/alerts/stream mediante fetch + ReadableStream para enviar Authorization Bearer.
 */

import { API_BASE_URL } from '../api/httpClient'

export interface AlertaGuardia {
  id: string
  documento_id: string
  episodio_id?: string | null
  prioridad: string
  fecha: string
  mensaje: string
}

export type AlertCallback = (alerta: AlertaGuardia) => void
export type ErrorCallback = (error: Error) => void

/**
 * Conecta al endpoint SSE de alertas médicas con soporte para Authorization Bearer
 * y reconexión automática en caso de interrupción de red.
 */
export function subscribeToAlertsStream(
  token: string,
  onAlert: AlertCallback,
  onError?: ErrorCallback
): () => void {
  let isAborted = false
  let abortController = new AbortController()

  async function connect() {
    if (isAborted) return

    try {
      const response = await fetch(`${API_BASE_URL}/alerts/stream`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'text/event-stream',
        },
        signal: abortController.signal,
      })

      if (!response.ok) {
        throw new Error(`Error en conexión SSE: ${response.status} ${response.statusText}`)
      }

      if (!response.body) {
        throw new Error('El servidor no retornó cuerpo de transmisión (ReadableStream).')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (!isAborted) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() ?? ''

        for (const block of events) {
          if (!block.trim() || block.startsWith(':')) {
            // Heartbeat o comentario SSE
            continue
          }

          const lines = block.split('\n')
          let eventType = 'message'
          let dataStr = ''

          for (const line of lines) {
            if (line.startsWith('event:')) {
              eventType = line.replace('event:', '').trim()
            } else if (line.startsWith('data:')) {
              dataStr += line.replace('data:', '').trim()
            }
          }

          if (eventType === 'ALERTA_GUARDIA_EMITIDA' && dataStr) {
            try {
              const alertData: AlertaGuardia = JSON.parse(dataStr)
              onAlert(alertData)
            } catch (parseError) {
              console.warn('[SSE] Error al parsear JSON de alerta:', parseError)
            }
          }
        }
      }
    } catch (err: any) {
      if (!isAborted && err.name !== 'AbortError') {
        if (onError) onError(err instanceof Error ? err : new Error(String(err)))
        // Intentar reconectar después de 4 segundos
        setTimeout(() => {
          if (!isAborted) {
            abortController = new AbortController()
            void connect()
          }
        }, 4000)
      }
    }
  }

  void connect()

  return () => {
    isAborted = true
    abortController.abort()
  }
}

/**
 * Emite un tono auditivo de alerta clínica usando la Web Audio API nativa.
 */
export function playEmergencyAlertSound(): void {
  try {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext
    if (!AudioCtx) return

    const ctx = new AudioCtx()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = 'sine'
    osc.frequency.setValueAtTime(880, ctx.currentTime) // Tono A5
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.35)

    gain.gain.setValueAtTime(0.18, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start()
    osc.stop(ctx.currentTime + 0.35)
  } catch {
    // Si el usuario no ha interactuado aún con el DOM, el navegador previene audio.
  }
}
