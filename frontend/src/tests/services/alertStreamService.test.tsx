import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  subscribeToAlertsStream,
  playEmergencyAlertSound,
  type AlertaGuardia,
} from '../../services/alertStreamService'

describe('alertStreamService - Servicio SSE de Alertas (FE-15 / Issue #72)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.unstubAllGlobals()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('se conecta al endpoint SSE con cabecera Authorization Bearer y procesa eventos', async () => {
    const mockAlert: AlertaGuardia = {
      id: 'alert-123',
      documento_id: 'DOC-123',
      prioridad: 'Urgente',
      fecha: '2026-10-20T12:00:00Z',
      mensaje: 'TEP agudo detectado',
    }

    const sseChunk = `event: ALERTA_GUARDIA_EMITIDA\ndata: ${JSON.stringify(mockAlert)}\n\n`
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(sseChunk))
        controller.close()
      },
    })

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: stream,
    })
    vi.stubGlobal('fetch', fetchMock)

    const onAlert = vi.fn()
    const unsubscribe = subscribeToAlertsStream('test-bearer-token', onAlert)

    await vi.waitFor(() => {
      expect(onAlert).toHaveBeenCalledWith(mockAlert)
    })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/alerts/stream'),
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer test-bearer-token',
          Accept: 'text/event-stream',
        },
      })
    )

    unsubscribe()
  })

  it('ignora comentarios SSE y heartbeats sin emitir alerta', async () => {
    const sseChunk = `: connected\n\n: heartbeat\n\n`
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(sseChunk))
        controller.close()
      },
    })

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, body: stream }))

    const onAlert = vi.fn()
    const unsubscribe = subscribeToAlertsStream('token', onAlert)

    await new Promise((r) => setTimeout(r, 50))
    expect(onAlert).not.toHaveBeenCalled()

    unsubscribe()
  })

  it('no lanza errores si playEmergencyAlertSound se ejecuta en entornos sin Web Audio API', () => {
    expect(() => playEmergencyAlertSound()).not.toThrow()
  })
})
