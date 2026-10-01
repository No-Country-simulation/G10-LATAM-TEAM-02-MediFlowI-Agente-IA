/**
 * MediFlow — Reglas Clínicas y de Autorización Hospitalaria
 */

/**
 * Roles autorizados exclusivamente para acceder y resolver Human-in-the-Loop (HITL)
 */
export const HITL_ALLOWED_ROLES: readonly string[] = ['COORDINADOR', 'ADMINISTRADOR']

/**
 * Determina si un rol de usuario puede acceder a la bandeja y resolución de HITL
 */
export function canAccessHitl(role?: string | null): boolean {
  if (!role) return false
  return HITL_ALLOWED_ROLES.includes(role.toUpperCase().trim())
}

/**
 * Calcula dinámicamente la edad en años a partir de la fecha de nacimiento (YYYY-MM-DD)
 */
export function calcularEdad(fechaNacimiento?: string | null, fechaReferencia: Date = new Date()): number | null {
  if (!fechaNacimiento) return null
  const nacimiento = new Date(fechaNacimiento)
  if (isNaN(nacimiento.getTime())) return null

  let edad = fechaReferencia.getFullYear() - nacimiento.getFullYear()
  const m = fechaReferencia.getMonth() - nacimiento.getMonth()
  if (m < 0 || (m === 0 && fechaReferencia.getDate() < nacimiento.getDate())) {
    edad--
  }
  return edad >= 0 ? edad : null
}

/**
 * Normaliza y valida la selección de género hospitalario (FEMENINO / MASCULINO)
 */
export function normalizarGenero(genero?: string | null): 'FEMENINO' | 'MASCULINO' | 'NO_ESPECIFICADO' {
  if (!genero) return 'NO_ESPECIFICADO'
  const normalizado = genero.toUpperCase().trim()
  if (normalizado === 'FEMENINO' || normalizado === 'F') return 'FEMENINO'
  if (normalizado === 'MASCULINO' || normalizado === 'M') return 'MASCULINO'
  return 'NO_ESPECIFICADO'
}
