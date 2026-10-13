/**
 * Formatea el tamaño de un archivo en bytes a una representación legible (MB o KB).
 */
export function formatFileSize(bytes: number): string {
  if (!bytes || bytes <= 0) return '0 KB'
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }
  return `${Math.round(bytes / 1024)} KB`
}

