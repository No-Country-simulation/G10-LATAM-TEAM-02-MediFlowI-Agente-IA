import { describe, it, expect } from 'vitest'
import { formatConfidence } from './formatConfidence'

describe('formatConfidence', () => {
  it('debe retornar nivel Alto para scores mayores o iguales a 80%', () => {
    const res1 = formatConfidence(0.85)
    expect(res1.percentage).toBe(85)
    expect(res1.level).toBe('Alta')
    expect(res1.variant).toBe('success')
    expect(res1.formattedText).toBe('85%')

    const res2 = formatConfidence(0.80)
    expect(res2.percentage).toBe(80)
    expect(res2.level).toBe('Alta')
  })

  it('debe retornar nivel Medio para scores entre 60% y 79%', () => {
    const res = formatConfidence(0.65)
    expect(res.percentage).toBe(65)
    expect(res.level).toBe('Media')
    expect(res.variant).toBe('warning')
    expect(res.badgeClass).toContain('bg-warning')
  })

  it('debe retornar nivel Bajo para scores menores al 60%', () => {
    const res = formatConfidence(0.45)
    expect(res.percentage).toBe(45)
    expect(res.level).toBe('Baja')
    expect(res.variant).toBe('danger')
  })

  it('debe manejar valores nulos, indefinidos o NaN retornando 0% y nivel Bajo', () => {
    expect(formatConfidence(null).percentage).toBe(0)
    expect(formatConfidence(null).level).toBe('Baja')
    expect(formatConfidence(undefined).percentage).toBe(0)
    expect(formatConfidence('no-es-numero').percentage).toBe(0)
  })

  it('debe procesar números enteros directos como 95%', () => {
    const res = formatConfidence(95)
    expect(res.percentage).toBe(95)
    expect(res.level).toBe('Alta')
  })
})
