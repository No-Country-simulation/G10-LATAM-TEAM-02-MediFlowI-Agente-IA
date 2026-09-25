type DateInput = string | number | Date | null | undefined

function parseDate(dateInput: DateInput): Date | null {
  if (!dateInput) return null
  const date = new Date(dateInput)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDate(dateInput: DateInput): string {
  const date = parseDate(dateInput)
  if (!date) return dateInput ? String(dateInput) : 'No identificado'
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}/${month}/${year} ${hours}:${minutes}`
}

export function formatDateShort(dateInput: DateInput): string {
  const date = parseDate(dateInput)
  if (!date) return dateInput ? String(dateInput) : 'No identificado'
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}/${date.getFullYear()}`
}
