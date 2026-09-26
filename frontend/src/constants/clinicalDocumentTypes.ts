export const CLINICAL_DOCUMENT_TYPES = [
  'Informe Clínico', 'Evolución Clínica', 'Epicrisis', 'Receta Médica',
  'Orden Médica', 'Orden de Procedimiento', 'Solicitud de Interconsulta',
  'Informe de Laboratorio', 'Informe de Estudio por Imágenes', 'Informe Quirúrgico',
  'Consentimiento Informado', 'Certificado Médico', 'Referencia y Contrarreferencia',
  'Registro de Vacunación', 'Otro',
] as const

export type ClinicalDocumentType = (typeof CLINICAL_DOCUMENT_TYPES)[number]

const normalizeKey = (value: string) => value.normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()

const aliases = new Map<string, ClinicalDocumentType>(
  CLINICAL_DOCUMENT_TYPES.map((type) => [normalizeKey(type), type]),
)

;[
  ['Analítica de Laboratorio', 'Informe de Laboratorio'],
  ['Resultado de Laboratorio', 'Informe de Laboratorio'],
  ['Informe de Estudio por Imagenes', 'Informe de Estudio por Imágenes'],
  ['Imagenología', 'Informe de Estudio por Imágenes'], ['Radiografía', 'Informe de Estudio por Imágenes'],
  ['Interconsulta', 'Solicitud de Interconsulta'], ['Alta Médica', 'Epicrisis'],
  ['Nota de Evolución', 'Evolución Clínica'], ['Prescripción Médica', 'Receta Médica'],
  ['Desconocido', 'Otro'], ['Error', 'Otro'],
].forEach(([alias, canonical]) => aliases.set(normalizeKey(alias), canonical as ClinicalDocumentType))

export function normalizeClinicalDocumentType(value?: string | null): ClinicalDocumentType {
  if (!value) return 'Otro'
  const key = normalizeKey(value)
  const exact = aliases.get(key)
  if (exact) return exact
  const match = [...aliases.entries()]
    .sort(([left], [right]) => right.length - left.length)
    .find(([alias]) => key.startsWith(`${alias} `) || ` ${key} `.includes(` ${alias} `))
  return match?.[1] ?? 'Otro'
}
