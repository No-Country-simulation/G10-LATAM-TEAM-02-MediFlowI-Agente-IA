import { describe, it, expect } from 'vitest'
import { formatDate, formatDateShort } from './formatDate'

describe('formatDate y formatDateShort', () => {
  it('debe formatear una fecha válida en formato completo DD/MM/YYYY HH:mm', () => {
    const d = new Date(2026, 8, 28, 14, 30) // Septiembre es mes 8 (0-indexed)
    const result = formatDate(d)
    expect(result).toBe('28/09/2026 14:30')
  })

  it('debe formatear una fecha válida en formato corto DD/MM/YYYY', () => {
    const d = new Date(2026, 8, 28)
    const result = formatDateShort(d)
    expect(result).toBe('28/09/2026')
  })

  it('debe devolver "No identificado" para entradas nulas o vacías', () => {
    expect(formatDate(null)).toBe('No identificado')
    expect(formatDate(undefined)).toBe('No identificado')
    expect(formatDateShort(null)).toBe('No identificado')
  })
})
