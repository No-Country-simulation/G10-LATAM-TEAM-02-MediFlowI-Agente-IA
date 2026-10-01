import { describe, it, expect } from 'vitest'
import { canAccessHitl, calcularEdad, normalizarGenero, HITL_ALLOWED_ROLES } from './clinicalRules'

describe('Reglas de Autorización HITL (canAccessHitl)', () => {
  it('permite el acceso exclusivo a los roles COORDINADOR y ADMINISTRADOR', () => {
    expect(canAccessHitl('COORDINADOR')).toBe(true)
    expect(canAccessHitl('ADMINISTRADOR')).toBe(true)
    expect(canAccessHitl('coordinador')).toBe(true)
    expect(canAccessHitl('administrador')).toBe(true)
  })

  it('bloquea el acceso a otros roles y valores nulos/vacíos', () => {
    expect(canAccessHitl('OPERADOR')).toBe(false)
    expect(canAccessHitl('MEDICO')).toBe(false)
    expect(canAccessHitl('SUPERVISOR')).toBe(false)
    expect(canAccessHitl('AUDITOR')).toBe(false)
    expect(canAccessHitl(null)).toBe(false)
    expect(canAccessHitl(undefined)).toBe(false)
    expect(canAccessHitl('')).toBe(false)
  })

  it('contiene exactamente los roles aprobados en HITL_ALLOWED_ROLES', () => {
    expect(HITL_ALLOWED_ROLES).toEqual(['COORDINADOR', 'ADMINISTRADOR'])
  })
})

describe('Cálculo Dinámico de Edad (calcularEdad)', () => {
  const refDate = new Date('2026-09-30T12:00:00Z')

  it('calcula la edad correcta antes y después del cumpleaños en el año de referencia', () => {
    // Ya cumplió años en 2026 (nacimiento en enero)
    expect(calcularEdad('1990-01-15', refDate)).toBe(36)
    // Aún no cumple años en 2026 (nacimiento en diciembre)
    expect(calcularEdad('1990-12-25', refDate)).toBe(35)
    // Cumpleaños exactamente hoy
    expect(calcularEdad('1996-09-30', refDate)).toBe(30)
  })

  it('maneja valores vacíos, nulos o fechas inválidas devolviendo null', () => {
    expect(calcularEdad(null, refDate)).toBeNull()
    expect(calcularEdad(undefined, refDate)).toBeNull()
    expect(calcularEdad('', refDate)).toBeNull()
    expect(calcularEdad('fecha-invalida', refDate)).toBeNull()
  })
})

describe('Normalización de Género Hospitalario (normalizarGenero)', () => {
  it('normaliza correctamente valores de género válidos', () => {
    expect(normalizarGenero('FEMENINO')).toBe('FEMENINO')
    expect(normalizarGenero('femenino')).toBe('FEMENINO')
    expect(normalizarGenero('F')).toBe('FEMENINO')
    expect(normalizarGenero('f')).toBe('FEMENINO')

    expect(normalizarGenero('MASCULINO')).toBe('MASCULINO')
    expect(normalizarGenero('masculino')).toBe('MASCULINO')
    expect(normalizarGenero('M')).toBe('MASCULINO')
    expect(normalizarGenero('m')).toBe('MASCULINO')
  })

  it('devuelve NO_ESPECIFICADO para valores vacíos, no binarios o no reconocidos', () => {
    expect(normalizarGenero(null)).toBe('NO_ESPECIFICADO')
    expect(normalizarGenero(undefined)).toBe('NO_ESPECIFICADO')
    expect(normalizarGenero('')).toBe('NO_ESPECIFICADO')
    expect(normalizarGenero('DESCONOCIDO')).toBe('NO_ESPECIFICADO')
  })
})
