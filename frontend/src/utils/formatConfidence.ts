export interface FormattedConfidence {
  percentage: number
  formattedText: string
  level: 'Alta' | 'Media' | 'Baja'
  variant: 'success' | 'warning' | 'danger'
  badgeClass: string
  progressClass: string
}

export function formatConfidence(score?: number | string | null): FormattedConfidence {
  const numericScore = Number(score)
  if (score === null || score === undefined || Number.isNaN(numericScore)) {
    return confidenceResult(0, 'Baja', 'danger')
  }

  const percentage = Math.round(numericScore > 0 && numericScore <= 1 ? numericScore * 100 : numericScore)
  if (percentage >= 80) return confidenceResult(percentage, 'Alta', 'success')
  if (percentage >= 60) return confidenceResult(percentage, 'Media', 'warning')
  return confidenceResult(percentage, 'Baja', 'danger')
}

function confidenceResult(
  percentage: number,
  level: FormattedConfidence['level'],
  variant: FormattedConfidence['variant'],
): FormattedConfidence {
  return {
    percentage,
    formattedText: `${percentage}%`,
    level,
    variant,
    badgeClass: variant === 'warning' ? 'bg-warning text-dark' : `bg-${variant}`,
    progressClass: `bg-${variant}`,
  }
}
