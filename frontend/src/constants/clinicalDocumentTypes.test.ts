import { describe, it, expect } from 'vitest'
import {
  normalizeClinicalDocumentType,
  CLINICAL_DOCUMENT_TYPES,
} from './clinicalDocumentTypes'

describe('clinicalDocumentTypes', () => {
  it('debe contener los 15 tipos de documentos clínicos estándar', () => {
    expect(CLINICAL_DOCUMENT_TYPES.length).toBe(15)
    expect(CLINICAL_DOCUMENT_TYPES).toContain('Informe Clínico')
    expect(CLINICAL_DOCUMENT_TYPES).toContain('Informe de Laboratorio')
    expect(CLINICAL_DOCUMENT_TYPES).toContain('Receta Médica')
    expect(CLINICAL_DOCUMENT_TYPES).toContain('Epicrisis')
  })

  it('debe normalizar sinónimos y variaciones al nombre canónico', () => {
    expect(normalizeClinicalDocumentType('Analítica de Laboratorio')).toBe('Informe de Laboratorio')
    expect(normalizeClinicalDocumentType('Resultado de Laboratorio')).toBe('Informe de Laboratorio')
    expect(normalizeClinicalDocumentType('Radiografía')).toBe('Informe de Estudio por Imágenes')
    expect(normalizeClinicalDocumentType('Alta Médica')).toBe('Epicrisis')
    expect(normalizeClinicalDocumentType('Prescripción Médica')).toBe('Receta Médica')
  })

  it('debe devolver "Otro" para valores no reconocidos o nulos', () => {
    expect(normalizeClinicalDocumentType(null)).toBe('Otro')
    expect(normalizeClinicalDocumentType(undefined)).toBe('Otro')
    expect(normalizeClinicalDocumentType('Desconocido')).toBe('Otro')
    expect(normalizeClinicalDocumentType('Factura Comercial')).toBe('Otro')
  })
})
