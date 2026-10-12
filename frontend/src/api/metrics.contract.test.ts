import { afterEach, describe, expect, expectTypeOf, it, vi } from 'vitest'
import type { MetricsResponse } from '../_generated/api'
import { apiRequest, API_BASE_URL } from './httpClient'

const examples: MetricsResponse[] = [
  { distribucion_prioridad: { Rojo: 2, Amarillo: 3, Verde: 5 }, tasa_hitl: 30, tiempo_promedio_ia_segundos: 2 },
  { distribucion_prioridad: { Rojo: 0, Amarillo: 0, Verde: 1 }, tasa_hitl: 0, tiempo_promedio_ia_segundos: 0 },
  { distribucion_prioridad: { Rojo: 0, Amarillo: 0, Verde: 0 }, tasa_hitl: null, tiempo_promedio_ia_segundos: null },
  { distribucion_prioridad: { Rojo: 0, Amarillo: 1, Verde: 0 }, tasa_hitl: 0, tiempo_promedio_ia_segundos: null },
  { distribucion_prioridad: { Rojo: 0, Amarillo: 0, Verde: 2 }, tasa_hitl: 0, tiempo_promedio_ia_segundos: 1.667 },
]

afterEach(() => { vi.unstubAllGlobals() })

describe('API-04 consumo de contrato fuera del dashboard', () => {
  it('conserva number|null requerido y los tres colores', () => {
    expectTypeOf<Pick<MetricsResponse, 'tasa_hitl'>>().toEqualTypeOf<{ tasa_hitl: number | null }>()
    expectTypeOf<Pick<MetricsResponse, 'tiempo_promedio_ia_segundos'>>().toEqualTypeOf<{ tiempo_promedio_ia_segundos: number | null }>()
    expectTypeOf<MetricsResponse['distribucion_prioridad']>().toEqualTypeOf<{ Rojo: number; Amarillo: number; Verde: number }>()
  })

  it.each(examples)('consume números y null sin sustituirlos por cero: %j', async (expected) => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(expected), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const actual = await apiRequest<MetricsResponse>('/metrics', { auth: false })
    expect(fetchMock).toHaveBeenCalledWith(`${API_BASE_URL}/metrics`, expect.any(Object))
    expect(actual).toEqual(expected)
    expect(Object.keys(actual).sort()).toEqual(['distribucion_prioridad', 'tasa_hitl', 'tiempo_promedio_ia_segundos'])
    expect(Object.keys(actual.distribucion_prioridad).sort()).toEqual(['Amarillo', 'Rojo', 'Verde'])
    for (const value of Object.values(actual.distribucion_prioridad)) {
      expect(Number.isInteger(value)).toBe(true)
      expect(value).toBeGreaterThanOrEqual(0)
    }
    if (actual.tasa_hitl === null) {
      expect(expected.tasa_hitl).toBeNull()
    } else {
      expectTypeOf(actual.tasa_hitl).toEqualTypeOf<number>()
      expect(actual.tasa_hitl).toBeGreaterThanOrEqual(0)
      expect(actual.tasa_hitl).toBeLessThanOrEqual(100)
    }
    if (actual.tiempo_promedio_ia_segundos === null) {
      expect(expected.tiempo_promedio_ia_segundos).toBeNull()
    } else {
      expectTypeOf(actual.tiempo_promedio_ia_segundos).toEqualTypeOf<number>()
      expect(actual.tiempo_promedio_ia_segundos).toBeGreaterThanOrEqual(0)
    }
  })
})
